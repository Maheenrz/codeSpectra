# analysis-engine/utils/iot_layer_detector.py

"""
IoT / Multi-Tier Cross-Layer Detector  (Generic Edition)
=========================================================
Detects whether a batch of files represents a multi-tier architecture and,
if so, finds function-name clones that span layers.

Design principle
----------------
Layers are identified from ARCHITECTURAL BEHAVIOUR — what the code does —
not from any specific SDK or vendor import.  This means the detector works
equally well for:
  • Android Wear OS  (Kotlin watch + Kotlin phone companion + Node cloud)
  • Fitbit OS        (JS device + JS companion + REST spec)
  • Arduino / MQTT   (C++ device + Python gateway + REST API)
  • AWS IoT          (C device SDK + Greengrass edge + Lambda)
  • Smart-home       (Raspberry Pi + Node bridge + Spring backend)
  • Any 3-tier web   (React + Express + OpenAPI spec)
  ...and anything else that fits the device → bridge → cloud pattern.

Layers
------
  DEVICE_LAYER   Hardware-facing code: reads sensors, drives actuators,
                 runs on-device OS (wearable, microcontroller, SBC, embedded).
  BRIDGE_LAYER   Protocol translator: moves data from device to cloud.
                 Could be a phone companion app, an edge gateway, or a
                 Bluetooth proxy — anything that forwards, not originates.
  CLOUD_LAYER    Server-side REST API, cloud function, or endpoint spec.
  WEB_FRONTEND   Browser/UI layer (React, Vue, Angular …).
  WEB_BACKEND    Server-side web framework with routes (Express, FastAPI …).

Token canonicalisation
----------------------
Function names are normalised to a shared camelCase form so that
  getHeartRate() in Kotlin   ←→  GET /heart-rate in a REST spec
  fetchActivity() in JS      ←→  getActivity() in Java   (synonym rule)
can be recognised as the same cross-layer feature.

Zero overhead for regular assignments
--------------------------------------
If no multi-layer signals are found in the batch, scan_batch_for_layers()
returns LayerContext(is_multi_layer=False) immediately.  Every subsequent
call in the analysis pipeline checks this flag first and exits early.

Usage
-----
    from utils.iot_layer_detector import scan_batch_for_layers, analyze_cross_layer_pair

    ctx   = scan_batch_for_layers(file_paths)     # call once per batch
    result = analyze_cross_layer_pair(a, b, ctx)  # call per pair
"""

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


# =============================================================================
# LAYER TYPES
# =============================================================================

class LayerType(Enum):
    DEVICE_LAYER  = "device_layer"    # wearable / microcontroller / sensor node
    BRIDGE_LAYER  = "bridge_layer"    # phone companion / edge gateway / MQTT broker
    CLOUD_LAYER   = "cloud_layer"     # REST API / cloud function / endpoint spec
    WEB_FRONTEND  = "web_frontend"    # browser UI (React, Vue, Angular …)
    WEB_BACKEND   = "web_backend"     # server-side web framework
    UNKNOWN       = "unknown"

    # Legacy aliases kept so any existing code that imports the old names keeps working
    @classmethod
    def WATCH_DEVICE(cls):  return cls.DEVICE_LAYER
    @classmethod
    def MOBILE_BRIDGE(cls): return cls.BRIDGE_LAYER
    @classmethod
    def CLOUD_REST(cls):    return cls.CLOUD_LAYER


# =============================================================================
# DATA STRUCTURES  (unchanged interface so analyzer.py needs no edits)
# =============================================================================

@dataclass
class NormalizedToken:
    canonical:   str
    original:    str
    layer:       LayerType
    line_number: int


@dataclass
class CrossLayerMatch:
    canonical:  str
    layer_a:    LayerType
    original_a: str
    line_a:     int
    layer_b:    LayerType
    original_b: str
    line_b:     int
    match_type: str   # "exact" | "synonym"


@dataclass
class CrossLayerResult:
    is_cross_layer:    bool
    layer_a:           LayerType
    layer_b:           LayerType
    matches:           list = field(default_factory=list)
    cross_layer_score: float = 0.0
    explanation:       str = ""

    def to_dict(self) -> dict:
        return {
            "is_cross_layer":    self.is_cross_layer,
            "layer_a":           self.layer_a.value,
            "layer_b":           self.layer_b.value,
            "cross_layer_score": round(self.cross_layer_score, 4),
            "explanation":       self.explanation,
            "matches": [
                {
                    "canonical":  m.canonical,
                    "match_type": m.match_type,
                    "layer_a":    m.layer_a.value,
                    "original_a": m.original_a,
                    "line_a":     m.line_a,
                    "layer_b":    m.layer_b.value,
                    "original_b": m.original_b,
                    "line_b":     m.line_b,
                }
                for m in self.matches
            ],
        }


@dataclass
class LayerContext:
    is_multi_layer: bool
    layer_map:      dict = field(default_factory=dict)
    reason:         str = ""

    @staticmethod
    def not_applicable() -> "LayerContext":
        return LayerContext(is_multi_layer=False, reason="No multi-layer signals detected")


# =============================================================================
# GENERIC LAYER DETECTION SIGNALS
# =============================================================================
# Signals are grouped by layer.  Each group has STRONG signals (SDK-specific,
# very reliable) and WEAK signals (generic keywords, only used as tiebreakers).
# ─────────────────────────────────────────────────────────────────────────────

# ── DEVICE LAYER ─────────────────────────────────────────────────────────────
# Anything that directly reads hardware / runs on-device OS.

_DEVICE_STRONG = re.compile(
    r"""
    # Android Wear OS
    WearableListenerService | WatchFaceService | WatchFaceStyle
    | Wearable\.getDataClient | Wearable\.getMessageClient
    | com\.google\.android\.gms\.wearable

    # Fitbit OS (JavaScript SDK)
    | import\s+.*from\s+["']fitbit
    | from\s+["']appbit["']
    | HeartRateSensor | BodyPresenceSensor | AccelerometerSensor

    # Arduino / embedded C++
    | \#include\s*[<"]Arduino\.h[>"]
    | \bdigitalWrite\s*\( | \banalogRead\s*\( | \bpinMode\s*\(
    | \bsetup\s*\(\s*\)\s*\{ | \bloop\s*\(\s*\)\s*\{

    # Raspberry Pi / MicroPython GPIO
    | import\s+RPi\.GPIO | from\s+gpiozero
    | machine\.Pin\s*\( | micropython | utime\.sleep

    # AWS IoT device SDK
    | AWSIoTMQTTClient | awsiot\.mqtt_connection_builder
    | from\s+AWSIoTPythonSDK

    # Azure IoT device SDK
    | IoTHubDeviceClient | from\s+azure\.iot\.device

    # Generic MQTT client (device side — publish-heavy)
    | paho\.mqtt | import\s+paho
    | mqtt\.Client\(\) | MQTTClient\s*\(

    # Zephyr RTOS / FreeRTOS
    | \bk_sleep\b | \bxTaskCreate\b | \bvTaskDelay\b | portTICK_PERIOD_MS

    # TensorFlow Lite / Edge AI (runs on device)
    | tflite\.Interpreter | tf\.lite\.Interpreter
    """,
    re.VERBOSE | re.MULTILINE,
)

_DEVICE_WEAK = re.compile(
    r"""
    SensorManager | SensorEvent | registerListener.*Sensor
    | readSensor | sensorValue | sampleRate
    | BLEPeripheral | BleAdvertiser | GATTServer
    """,
    re.VERBOSE | re.MULTILINE,
)


# ── BRIDGE LAYER ─────────────────────────────────────────────────────────────
# Mediates between device and cloud: phone companion, edge gateway, MQTT broker.

_BRIDGE_STRONG = re.compile(
    r"""
    # Android Wear OS phone companion
    DataClient\.OnDataChangedListener | ChannelClient\.Channel
    | CapabilityClient | MessageClient\.OnMessageReceivedListener

    # Fitbit JS companion
    | peerSocket\. | companionSettings | settingsStorage | me\.permissions

    # AWS Greengrass (edge)
    | greengrass | aws_greengrass | GreengrassCoreIPCClientV2

    # Azure IoT Edge
    | azure\.iot\.edge | IoTHubModuleClient

    # MQTT broker / subscriber (bridge subscribes and forwards)
    | mqtt\.subscribe | client\.subscribe\s*\( | on_message\s*=
    | mosquitto | MQTT\.subscribe

    # Generic BLE central (bridge connects to peripheral device)
    | BleManager | BluetoothGatt\b | BluetoothLeScanner
    | CoreBluetooth | CBCentralManager
    """,
    re.VERBOSE | re.MULTILINE,
)

_BRIDGE_WEAK = re.compile(
    r"""
    \brelay\b | \bforward\b | \bbridge\b | \bgateway\b
    | \bproxy\b | \bmediator\b | \bcompanion\b
    """,
    re.VERBOSE | re.MULTILINE,
)


# ── CLOUD LAYER ───────────────────────────────────────────────────────────────
# REST API endpoints, cloud functions, endpoint specs.

_CLOUD_STRONG = re.compile(
    r"""
    # OpenAPI / Swagger spec
    openapi\s*: | swagger\s*: | ^paths\s*:

    # Express / Node.js routes
    | router\.(get|post|put|delete|patch)\s*\(
    | app\.(get|post|put|delete|patch)\s*\(

    # FastAPI / Flask / Starlette
    | @app\.(get|post|put|delete|patch)\s*\(
    | @router\.(get|post|put|delete|patch)\s*\(

    # Spring Boot
    | @GetMapping | @PostMapping | @PutMapping | @DeleteMapping
    | @RequestMapping | @RestController | @Controller

    # Django REST
    | @api_view | class.*APIView | class.*ViewSet
    | urlpatterns\s*= | path\s*\(.*views\.

    # Raw HTTP method lines (endpoint spec files)
    | \b(?:GET|POST|PUT|DELETE|PATCH)\s+/\S+

    # AWS Lambda handler
    | def\s+lambda_handler\s*\(\s*event
    | exports\.handler\s*= | module\.exports\.handler

    # Azure / GCP cloud functions
    | azure\.functions | @app\.function_name\s*\(
    | functions\.HttpRequest | functions\.HttpResponse

    # GraphQL server
    | ApolloServer | makeExecutableSchema | typeDefs.*resolvers
    """,
    re.VERBOSE | re.MULTILINE,
)


# ── WEB FRONTEND ──────────────────────────────────────────────────────────────

_WEB_FRONTEND = re.compile(
    r"""
    import\s+React | from\s+["']react["']
    | useState\s*\( | useEffect\s*\(
    | from\s+["']vue["'] | createApp\s*\(
    | ng-app | @Component\s*\({
    | import.*from\s+["']@angular
    """,
    re.VERBOSE | re.MULTILINE,
)


# ── WEB BACKEND ───────────────────────────────────────────────────────────────
# Node.js / Express backend that doesn't show route definitions
# (those are caught by _CLOUD_STRONG already).

_WEB_BACKEND = re.compile(
    r"""
    require\s*\(\s*["']express["']\s*\)
    | require\s*\(\s*["']fastify["']\s*\)
    | require\s*\(\s*["']koa["']\s*\)
    | module\.exports
    """,
    re.VERBOSE | re.MULTILINE,
)


# Combinations of layer types that together indicate a multi-tier architecture
_MULTI_LAYER_COMBOS = [
    {LayerType.DEVICE_LAYER,  LayerType.BRIDGE_LAYER},
    {LayerType.DEVICE_LAYER,  LayerType.CLOUD_LAYER},
    {LayerType.DEVICE_LAYER,  LayerType.WEB_BACKEND},
    {LayerType.BRIDGE_LAYER,  LayerType.CLOUD_LAYER},
    {LayerType.BRIDGE_LAYER,  LayerType.WEB_BACKEND},
    {LayerType.WEB_FRONTEND,  LayerType.WEB_BACKEND},
    {LayerType.WEB_FRONTEND,  LayerType.CLOUD_LAYER},
]


# =============================================================================
# FILEPATH HINTS  (checked before content heuristics — most reliable)
# =============================================================================

# Maps path substrings to LayerType.  Checked in order; first match wins.
_PATH_HINTS: list[tuple[list[str], LayerType]] = [
    # Device / wearable
    (["wear_app/", "/device/", "wear/src", "_watch", "watch_", "wearable/app",
      "embedded/", "firmware/", "sensor/", "/microcontroller"],
     LayerType.DEVICE_LAYER),

    # Bridge / companion / gateway
    (["phone_app/", "/companion", "bridge/", "gateway/", "handheld/",
      "mobile/", "edge/", "relay/"],
     LayerType.BRIDGE_LAYER),

    # Cloud / API
    (["cloud/", "server/", "backend/", "api/", "lambda/",
      "cloud_layer/", "cloud_server/", "functions/"],
     LayerType.CLOUD_LAYER),

    # Web frontend
    (["frontend/", "client/", "ui/", "webapp/", "pages/",
      "components/", "views/"],
     LayerType.WEB_FRONTEND),
]

# File extensions that are always REST/spec files regardless of content
_SPEC_EXTS = {".yaml", ".yml", ".raml", ".json"}


def _detect_layer_from_content(source: str, filepath: str = "") -> LayerType:
    """
    Classify a file into its architectural layer.
    Uses filepath hints first (strongest), then content patterns.
    """
    fp = filepath.lower()
    ext = Path(fp).suffix

    # ── 1. Extension-based overrides ────────────────────────────────────────
    if ext in _SPEC_EXTS and ("openapi" in fp or "swagger" in fp or "api" in fp or "route" in fp):
        return LayerType.CLOUD_LAYER

    # ── 2. Path-based hints ──────────────────────────────────────────────────
    for hints, layer in _PATH_HINTS:
        if any(h in fp for h in hints):
            return layer

    # OpenAPI YAML anywhere
    if ext in {".yaml", ".yml"} and re.search(r'^\s*(?:openapi|swagger|paths)\s*:', source, re.MULTILINE):
        return LayerType.CLOUD_LAYER

    # ── 3. Strong content signals ────────────────────────────────────────────
    if _DEVICE_STRONG.search(source):
        return LayerType.DEVICE_LAYER

    if _BRIDGE_STRONG.search(source):
        return LayerType.BRIDGE_LAYER

    if _CLOUD_STRONG.search(source):
        return LayerType.CLOUD_LAYER

    if _WEB_FRONTEND.search(source):
        return LayerType.WEB_FRONTEND

    if _WEB_BACKEND.search(source):
        return LayerType.WEB_BACKEND

    # ── 4. Weak fallback signals (only when nothing stronger fired) ──────────
    if _DEVICE_WEAK.search(source):
        return LayerType.DEVICE_LAYER

    if _BRIDGE_WEAK.search(source):
        return LayerType.BRIDGE_LAYER

    return LayerType.UNKNOWN


# =============================================================================
# BATCH-LEVEL SCAN  — called once per job, O(n)
# =============================================================================

def scan_batch_for_layers(file_paths: list[str]) -> LayerContext:
    """
    Scan all files in the batch once and decide if multi-layer analysis
    is worth running.  Returns LayerContext(is_multi_layer=False) instantly
    for ordinary student assignments.
    """
    layer_map:    dict[str, LayerType] = {}
    layers_found: set[LayerType]       = set()

    for fp in file_paths:
        try:
            source = Path(fp).read_text(encoding="utf-8", errors="ignore")
            layer  = _detect_layer_from_content(source, fp)
            layer_map[fp] = layer
            if layer != LayerType.UNKNOWN:
                layers_found.add(layer)
        except OSError:
            layer_map[fp] = LayerType.UNKNOWN

    for combo in _MULTI_LAYER_COMBOS:
        if combo.issubset(layers_found):
            names = " + ".join(l.value for l in layers_found if l != LayerType.UNKNOWN)
            return LayerContext(is_multi_layer=True, layer_map=layer_map,
                                reason=f"Detected layers: {names}")

    return LayerContext.not_applicable()


# =============================================================================
# TOKEN EXTRACTION — multi-language, language-auto-detected
# =============================================================================

# Synonym normalization: collapse semantic variants to a shared canonical name
_SYNONYM_PATTERNS = [
    # get synonyms
    (re.compile(r'^fetch([A-Z])'),      r'get\1'),
    (re.compile(r'^retrieve([A-Z])'),   r'get\1'),
    (re.compile(r'^load([A-Z])'),       r'get\1'),
    (re.compile(r'^read([A-Z])'),       r'get\1'),
    (re.compile(r'^query([A-Z])'),      r'get\1'),

    # send synonyms
    (re.compile(r'^push([A-Z])'),       r'send\1'),
    (re.compile(r'^upload([A-Z])'),     r'send\1'),
    (re.compile(r'^transmit([A-Z])'),   r'send\1'),
    (re.compile(r'^publish([A-Z])'),    r'send\1'),
    (re.compile(r'^emit([A-Z])'),       r'send\1'),

    # post/create synonyms
    (re.compile(r'^log([A-Z])'),        r'post\1'),
    (re.compile(r'^record([A-Z])'),     r'post\1'),
    (re.compile(r'^submit([A-Z])'),     r'post\1'),
    (re.compile(r'^save([A-Z])'),       r'post\1'),

    # update synonyms
    (re.compile(r'^modify([A-Z])'),     r'update\1'),
    (re.compile(r'^edit([A-Z])'),       r'update\1'),
    (re.compile(r'^patch([A-Z])'),      r'update\1'),

    # sync synonyms
    (re.compile(r'^synchronize([A-Z])'), r'sync\1'),
]


def _to_canonical(name: str) -> str:
    """Normalise a function name by collapsing synonyms to a shared root."""
    canonical = name.strip()
    for pattern, replacement in _SYNONYM_PATTERNS:
        canonical = pattern.sub(replacement, canonical)
    return canonical


def _rest_to_canonical(method: str, path: str) -> str:
    """
    Convert a REST endpoint into a camelCase canonical function name.

        GET  /heart-rate          → getHeartRate
        POST /activity/log        → postActivityLog
        GET  /user/{id}/profile   → getUserProfile   (path params stripped)
        DELETE /devices/:id       → deleteDevices
    """
    method = method.strip().lower()

    # Strip path parameters — {param}, [param], :param
    path = re.sub(r'[\{\[][^\}\]]*[\}\]]', '', path)
    path = re.sub(r':[a-zA-Z0-9_]+', '', path)

    segments = [s for s in path.strip('/').split('/') if s.strip()]

    def _pascal(seg: str) -> str:
        return ''.join(w.capitalize() for w in re.split(r'[-_]', seg))

    return method + ''.join(_pascal(s) for s in segments)


# ── Language-specific function-name patterns ─────────────────────────────────

# JavaScript / TypeScript
_JS_FUNC = [
    re.compile(r'(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('),
    re.compile(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?\('),
    re.compile(r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*(?:async\s*)?function'),
    re.compile(r'(?:async\s+)?([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{'),   # method shorthand
]
_JS_API_CALL = re.compile(r'\b((?:get|fetch|send|post|put|delete|sync|update)[A-Z][a-zA-Z0-9_]*)\s*\(')

# Kotlin
_KT_FUNC = re.compile(r'\bfun\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(<]')

# Java (rough — catches most method declarations without a full AST)
_JAVA_FUNC = re.compile(
    r'(?:public|private|protected|static|void|int|long|boolean|String|List|Map|'
    r'float|double|byte|override|suspend|synchronized)\s+'
    r'(?:static\s+)?(?:final\s+)?'
    r'(?:[\w<>\[\],\s]+\s+)?'          # return type (optional, tolerant)
    r'([a-z][a-zA-Z0-9_]*)\s*\('       # method name starting lowercase
)

# Python
_PY_FUNC = re.compile(r'^\s*(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)

# C / C++
_C_FUNC = re.compile(
    r'^(?:static\s+|inline\s+|extern\s+)?'
    r'(?:void|int|long|unsigned|char|float|double|bool|auto|size_t|uint\w*)\s+'
    r'([a-z][a-zA-Z0-9_]*)\s*\(',
    re.MULTILINE,
)

# REST endpoint lines
_REST_LINE  = re.compile(r'\b(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\'"]+)', re.IGNORECASE)
_AXIOS_CALL = re.compile(r'axios\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
_FETCH_CALL = re.compile(r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)   # fetch(url) — method inferred as GET

# Noise — too short or too generic to be meaningful signals
_NOISE = frozenset([
    'app', 'cb', 'fn', 'e', 'err', 'res', 'req', 'next', 'done',
    'main', 'run', 'init', 'setup', 'loop', 'on', 'off', 'ok',
    'get', 'set', 'add', 'del', 'it', 'test', 'log',
])


def _is_code_kotlin(source: str) -> bool:
    return bool(_KT_FUNC.search(source)) and 'function ' not in source


def _is_code_python(source: str) -> bool:
    return bool(_PY_FUNC.search(source))


def _extract_tokens(source: str, layer: LayerType, filepath: str = "") -> list[NormalizedToken]:
    """
    Auto-detect the source language and extract normalised function tokens.
    Works for JS/TS, Kotlin, Java, Python, C/C++, and REST specs/YAML.
    """
    ext  = Path(filepath).suffix.lower() if filepath else ""
    seen: set[str] = set()
    tokens: list[NormalizedToken] = []

    def _add(original: str, line_no: int) -> None:
        name = original.strip()
        if len(name) < 3 or name.lower() in _NOISE:
            return
        canonical = _to_canonical(name)
        if canonical not in seen:
            seen.add(canonical)
            tokens.append(NormalizedToken(canonical, name, layer, line_no))

    # ── REST spec / YAML — endpoint extraction ───────────────────────────────
    if layer == LayerType.CLOUD_LAYER or ext in {".yaml", ".yml", ".raml"}:
        for line_no, line in enumerate(source.splitlines(), 1):
            for m in _REST_LINE.finditer(line):
                canon = _rest_to_canonical(m.group(1), m.group(2))
                if len(canon) >= 4 and canon not in seen:
                    seen.add(canon)
                    tokens.append(NormalizedToken(
                        canon, f"{m.group(1).upper()} {m.group(2)}", layer, line_no))
            for m in _AXIOS_CALL.finditer(line):
                canon = _rest_to_canonical(m.group(1), m.group(2))
                if len(canon) >= 4 and canon not in seen:
                    seen.add(canon)
                    tokens.append(NormalizedToken(
                        canon, f"axios.{m.group(1)}('{m.group(2)}')", layer, line_no))
        if tokens:
            return tokens  # pure REST file — no need to continue

    # ── Kotlin ───────────────────────────────────────────────────────────────
    if ext in {".kt", ".kts"} or (ext not in {".js", ".ts", ".jsx", ".tsx", ".java", ".py", ".c", ".cpp", ".h", ".hpp"} and _is_code_kotlin(source)):
        for line_no, line in enumerate(source.splitlines(), 1):
            m = _KT_FUNC.search(line)
            if m:
                _add(m.group(1), line_no)
        return tokens

    # ── Python ───────────────────────────────────────────────────────────────
    if ext == ".py" or (ext == "" and _is_code_python(source)):
        for line_no, line in enumerate(source.splitlines(), 1):
            m = _PY_FUNC.search(line)
            if m:
                _add(m.group(1), line_no)
        return tokens

    # ── C / C++ ──────────────────────────────────────────────────────────────
    if ext in {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"}:
        for line_no, line in enumerate(source.splitlines(), 1):
            m = _C_FUNC.search(line)
            if m:
                _add(m.group(1), line_no)
        return tokens

    # ── Java ─────────────────────────────────────────────────────────────────
    if ext == ".java":
        for line_no, line in enumerate(source.splitlines(), 1):
            m = _JAVA_FUNC.search(line)
            if m:
                _add(m.group(1), line_no)
        return tokens

    # ── JavaScript / TypeScript (default fallback) ───────────────────────────
    for line_no, line in enumerate(source.splitlines(), 1):
        for pattern in _JS_FUNC:
            m = pattern.search(line)
            if m:
                _add(m.group(1), line_no)
                break
        for m in _JS_API_CALL.finditer(line):
            _add(m.group(1), line_no)
        for m in _REST_LINE.finditer(line):
            canon = _rest_to_canonical(m.group(1), m.group(2))
            if len(canon) >= 4 and canon not in seen:
                seen.add(canon)
                tokens.append(NormalizedToken(
                    canon, f"{m.group(1).upper()} {m.group(2)}", layer, line_no))

    return tokens


# Keep old name as alias so existing tests that call it still work
def _extract_tokens_for_layer(source: str, layer: LayerType) -> list[NormalizedToken]:
    return _extract_tokens(source, layer)


# =============================================================================
# PAIR-LEVEL CROSS-LAYER ANALYSIS
# =============================================================================

def analyze_cross_layer_pair(
    file_a:  str,
    file_b:  str,
    context: LayerContext,
) -> Optional[CrossLayerResult]:
    """
    Check if two files are from different architectural layers and, if so,
    find the shared canonical function/feature names.

    Returns None if the batch context says this is not a multi-layer codebase
    (fast-exit for ordinary student assignments).
    """
    if not context.is_multi_layer:
        return None

    layer_a = context.layer_map.get(file_a, LayerType.UNKNOWN)
    layer_b = context.layer_map.get(file_b, LayerType.UNKNOWN)

    if layer_a == layer_b:
        return None

    if layer_a == LayerType.UNKNOWN and layer_b == LayerType.UNKNOWN:
        return None

    try:
        source_a = Path(file_a).read_text(encoding="utf-8", errors="ignore")
        source_b = Path(file_b).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    tokens_a = _extract_tokens(source_a, layer_a, file_a)
    tokens_b = _extract_tokens(source_b, layer_b, file_b)

    if not tokens_a or not tokens_b:
        return CrossLayerResult(
            is_cross_layer=True,
            layer_a=layer_a, layer_b=layer_b,
            matches=[], cross_layer_score=0.0,
            explanation="Layers detected but no extractable function tokens found.",
        )

    map_a = {t.canonical: t for t in tokens_a}
    map_b = {t.canonical: t for t in tokens_b}

    shared = set(map_a) & set(map_b)
    matches = [
        CrossLayerMatch(
            canonical  = canon,
            layer_a    = map_a[canon].layer,
            original_a = map_a[canon].original,
            line_a     = map_a[canon].line_number,
            layer_b    = map_b[canon].layer,
            original_b = map_b[canon].original,
            line_b     = map_b[canon].line_number,
            match_type = "exact" if map_a[canon].original == map_b[canon].original else "synonym",
        )
        for canon in sorted(shared)
    ]

    smaller = min(len(map_a), len(map_b))
    score   = round(len(matches) / smaller, 4) if smaller > 0 else 0.0

    if matches:
        names  = ", ".join(m.canonical for m in matches[:3])
        suffix = f" (+{len(matches)-3} more)" if len(matches) > 3 else ""
        explanation = (
            f"Cross-layer match: {layer_a.value} ↔ {layer_b.value}. "
            f"Shared features: {names}{suffix}."
        )
    else:
        explanation = (
            f"Different layers ({layer_a.value} ↔ {layer_b.value}) "
            f"but no shared function names found."
        )

    return CrossLayerResult(
        is_cross_layer    = True,
        layer_a           = layer_a,
        layer_b           = layer_b,
        matches           = matches,
        cross_layer_score = score,
        explanation       = explanation,
    )


# =============================================================================
# PUBLIC ALIASES — keep old Fitbit-era symbol names importable
# (the test file imports _detect_layer_from_content, _rest_to_canonical,
#  _to_canonical_js — all kept working below)
# =============================================================================

def detect_layer_from_content(source: str, filepath: str = "") -> LayerType:
    return _detect_layer_from_content(source, filepath)

# Old name alias used in tests
_to_canonical_js = _to_canonical
