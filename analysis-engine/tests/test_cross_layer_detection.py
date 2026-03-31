# analysis-engine/tests/test_cross_layer_detection.py

"""
Cross-Layer Detection Tests  (Generic Edition)
===============================================
Tests cover the generic, platform-agnostic detector.  Individual test classes
target specific architectures to prove the detector is not vendor-locked:

  TestRestToCanonical       — REST path → camelCase canonical name
  TestSynonymNormalisation  — fetchX/retrieveX → getX, pushX/uploadX → sendX, etc.
  TestLayerDetection        — generic signals for device / bridge / cloud layers
  TestPlatformSpecific      — Wear OS, Fitbit, Arduino, MQTT, AWS IoT, FastAPI, Spring
  TestBatchScan             — scan_batch_for_layers gating
  TestCrossLayerPairAnalysis — end-to-end pair-level analysis with sample files
  TestSampleFiles            — runs against the actual iot_sample/ directory

Run:
    cd analysis-engine
    python -m pytest tests/test_cross_layer_detection.py -v
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.iot_layer_detector import (
    _detect_layer_from_content,
    _rest_to_canonical,
    _to_canonical,
    _to_canonical_js,          # legacy alias — must still work
    scan_batch_for_layers,
    analyze_cross_layer_pair,
    LayerType,
)

# Path to the bundled 3-tier sample
SAMPLE_DIR  = Path(__file__).parent / "iot_sample"
DEVICE_FILE = SAMPLE_DIR / "device_layer"  / "HealthSensorService.kt"
BRIDGE_FILE = SAMPLE_DIR / "bridge_layer"  / "PhoneGatewayService.kt"
CLOUD_FILE  = SAMPLE_DIR / "cloud_layer"   / "health_api_server.js"


# =============================================================================
# HELPERS
# =============================================================================

def _tmp(content: str, suffix: str = ".js") -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
    f.write(content)
    f.close()
    return f.name


# =============================================================================
# REST CANONICALISATION
# =============================================================================

class TestRestToCanonical:
    def test_get_single_segment(self):
        assert _rest_to_canonical("GET", "/heart-rate") == "getHeartRate"

    def test_get_nested(self):
        assert _rest_to_canonical("GET", "/user/profile") == "getUserProfile"

    def test_post_nested(self):
        assert _rest_to_canonical("POST", "/activity/log") == "postActivityLog"

    def test_get_sleep_data(self):
        assert _rest_to_canonical("GET", "/sleep/data") == "getSleepData"

    def test_path_param_curly(self):
        result = _rest_to_canonical("GET", "/user/{id}/profile")
        assert result == "getUserProfile"

    def test_path_param_colon(self):
        result = _rest_to_canonical("DELETE", "/devices/:deviceId/alarms")
        assert result == "deleteDevicesAlarms"

    def test_case_insensitive_method(self):
        assert _rest_to_canonical("get", "/sleep") == "getSleep"

    def test_delete_nested(self):
        assert _rest_to_canonical("DELETE", "/devices/tracker/alarms") == "deleteDevicesTrackerAlarms"

    def test_put_endpoint(self):
        assert _rest_to_canonical("PUT", "/user/profile") == "putUserProfile"


# =============================================================================
# SYNONYM NORMALISATION
# =============================================================================

class TestSynonymNormalisation:
    # get synonyms
    def test_fetch_to_get(self):
        assert _to_canonical("fetchHeartRate") == "getHeartRate"

    def test_retrieve_to_get(self):
        assert _to_canonical("retrieveActivity") == "getActivity"

    def test_read_to_get(self):
        assert _to_canonical("readSensor") == "getSensor"

    def test_query_to_get(self):
        assert _to_canonical("queryUserProfile") == "getUserProfile"

    def test_load_to_get(self):
        assert _to_canonical("loadSleepData") == "getSleepData"

    # send synonyms
    def test_push_to_send(self):
        assert _to_canonical("pushData") == "sendData"

    def test_upload_to_send(self):
        assert _to_canonical("uploadMetrics") == "sendMetrics"

    def test_transmit_to_send(self):
        assert _to_canonical("transmitReading") == "sendReading"

    def test_publish_to_send(self):
        assert _to_canonical("publishEvent") == "sendEvent"

    # post/create synonyms
    def test_log_to_post(self):
        assert _to_canonical("logActivity") == "postActivity"

    def test_record_to_post(self):
        assert _to_canonical("recordHeartRate") == "postHeartRate"

    def test_submit_to_post(self):
        assert _to_canonical("submitForm") == "postForm"

    # update synonyms
    def test_modify_to_update(self):
        assert _to_canonical("modifyProfile") == "updateProfile"

    def test_edit_to_update(self):
        assert _to_canonical("editSettings") == "updateSettings"

    # unchanged
    def test_already_canonical(self):
        assert _to_canonical("getHeartRate") == "getHeartRate"

    def test_no_match_unchanged(self):
        assert _to_canonical("calculateBMI") == "calculateBMI"

    def test_legacy_alias_works(self):
        # _to_canonical_js is a legacy alias — must still be importable and correct
        assert _to_canonical_js("fetchHeartRate") == "getHeartRate"


# =============================================================================
# GENERIC LAYER DETECTION
# =============================================================================

class TestLayerDetection:
    """
    The detector should identify layers from architectural signals regardless
    of which specific platform the code is for.
    """

    # ── Device layer signals ─────────────────────────────────────────────────
    def test_wearos_device(self):
        src = "class X : WearableListenerService() { fun onDataChanged() {} }"
        assert _detect_layer_from_content(src) == LayerType.DEVICE_LAYER

    def test_fitbit_device(self):
        src = 'import { HeartRateSensor } from "fitbit-sensors";'
        assert _detect_layer_from_content(src) == LayerType.DEVICE_LAYER

    def test_arduino_device(self):
        src = '#include <Arduino.h>\nvoid setup(){}\nvoid loop(){ digitalWrite(13, HIGH); }'
        assert _detect_layer_from_content(src) == LayerType.DEVICE_LAYER

    def test_raspberrypi_device(self):
        src = "import RPi.GPIO as GPIO\nGPIO.setup(17, GPIO.OUT)"
        assert _detect_layer_from_content(src) == LayerType.DEVICE_LAYER

    def test_micropython_device(self):
        src = "import machine\npin = machine.Pin(2, machine.Pin.OUT)\nutime.sleep(1)"
        assert _detect_layer_from_content(src) == LayerType.DEVICE_LAYER

    def test_paho_mqtt_device(self):
        src = "import paho.mqtt.client as mqtt\nclient = mqtt.Client()\nclient.publish('topic', 'val')"
        assert _detect_layer_from_content(src) == LayerType.DEVICE_LAYER

    def test_aws_iot_device(self):
        src = "from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient"
        assert _detect_layer_from_content(src) == LayerType.DEVICE_LAYER

    def test_path_hint_wear_app(self):
        src = "// some device code"
        assert _detect_layer_from_content(src, "wear_app/DataService.kt") == LayerType.DEVICE_LAYER

    def test_path_hint_embedded(self):
        src = "// some c code"
        assert _detect_layer_from_content(src, "firmware/main.c") == LayerType.DEVICE_LAYER

    # ── Bridge layer signals ─────────────────────────────────────────────────
    def test_wearos_bridge(self):
        src = "class X : DataClient.OnDataChangedListener { override fun onDataChanged() {} }"
        assert _detect_layer_from_content(src) == LayerType.BRIDGE_LAYER

    def test_fitbit_companion(self):
        src = "import { peerSocket } from 'messaging';\npeerSocket.send({});"
        assert _detect_layer_from_content(src) == LayerType.BRIDGE_LAYER

    def test_mqtt_subscriber_bridge(self):
        src = "client.subscribe('sensors/+/heartrate')\ndef on_message(client, userdata, msg):\n    forward(msg)"
        assert _detect_layer_from_content(src) == LayerType.BRIDGE_LAYER

    def test_greengrass_bridge(self):
        src = "from greengrasssdk import client as greengrass\nipc = GreengrassCoreIPCClientV2()"
        assert _detect_layer_from_content(src) == LayerType.BRIDGE_LAYER

    def test_path_hint_companion(self):
        src = "// bridge code"
        assert _detect_layer_from_content(src, "companion/index.js") == LayerType.BRIDGE_LAYER

    def test_path_hint_gateway(self):
        src = "// gateway code"
        assert _detect_layer_from_content(src, "gateway/main.py") == LayerType.BRIDGE_LAYER

    # ── Cloud layer signals ──────────────────────────────────────────────────
    def test_express_routes(self):
        src = "const express = require('express');\nrouter.get('/heart-rate', handler);"
        assert _detect_layer_from_content(src) == LayerType.CLOUD_LAYER

    def test_fastapi_routes(self):
        src = "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef health(): pass"
        assert _detect_layer_from_content(src) == LayerType.CLOUD_LAYER

    def test_flask_routes(self):
        src = "@app.post('/data')\ndef post_data(): pass"
        assert _detect_layer_from_content(src) == LayerType.CLOUD_LAYER

    def test_spring_rest(self):
        src = "@RestController\n@GetMapping('/user/profile')\npublic UserDto getUser() {}"
        assert _detect_layer_from_content(src) == LayerType.CLOUD_LAYER

    def test_django_urls(self):
        src = "urlpatterns = [path('api/heart-rate/', views.heart_rate)]"
        assert _detect_layer_from_content(src) == LayerType.CLOUD_LAYER

    def test_lambda_handler(self):
        src = "def lambda_handler(event, context):\n    return {'statusCode': 200}"
        assert _detect_layer_from_content(src) == LayerType.CLOUD_LAYER

    def test_raw_rest_spec(self):
        src = "GET /heart-rate\nPOST /activity/log\nGET /sleep/data"
        assert _detect_layer_from_content(src) == LayerType.CLOUD_LAYER

    def test_openapi_yaml(self):
        src = "openapi: 3.0.0\npaths:\n  /heart-rate:\n    get:\n      summary: Get BPM"
        assert _detect_layer_from_content(src) == LayerType.CLOUD_LAYER

    def test_path_hint_cloud_layer(self):
        src = "// cloud server"
        assert _detect_layer_from_content(src, "cloud_layer/server.js") == LayerType.CLOUD_LAYER

    def test_path_hint_backend(self):
        src = "// backend code"
        assert _detect_layer_from_content(src, "backend/server.js") == LayerType.CLOUD_LAYER

    # ── Web frontend ─────────────────────────────────────────────────────────
    def test_react_frontend(self):
        src = "import React from 'react';\nimport { useState } from 'react';"
        assert _detect_layer_from_content(src) == LayerType.WEB_FRONTEND

    # ── Non-IoT code is UNKNOWN ───────────────────────────────────────────────
    def test_plain_cpp_is_unknown(self):
        src = "#include<iostream>\nint main(){std::cout<<42;return 0;}"
        layer = _detect_layer_from_content(src)
        assert layer == LayerType.UNKNOWN

    def test_plain_java_is_unknown(self):
        src = "public class Main { public static void main(String[] args) { System.out.println(42); } }"
        layer = _detect_layer_from_content(src)
        assert layer == LayerType.UNKNOWN


# =============================================================================
# BATCH SCAN — multi-layer gating
# =============================================================================

class TestBatchScan:
    def test_regular_cpp_not_multi_layer(self):
        f1 = _tmp("#include<iostream>\nint main(){return 0;}", ".cpp")
        f2 = _tmp("#include<iostream>\nvoid sort(){}", ".cpp")
        try:
            ctx = scan_batch_for_layers([f1, f2])
            assert ctx.is_multi_layer is False
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_wearos_device_plus_bridge_is_multi_layer(self):
        device_src  = "class X : WearableListenerService() { fun getHeartRate() {} }"
        bridge_src  = "class Y : DataClient.OnDataChangedListener { override fun onDataChanged() {} }"
        f1 = _tmp(device_src,  ".kt")
        f2 = _tmp(bridge_src,  ".kt")
        try:
            ctx = scan_batch_for_layers([f1, f2])
            assert ctx.is_multi_layer is True
            assert ctx.layer_map[f1] == LayerType.DEVICE_LAYER
            assert ctx.layer_map[f2] == LayerType.BRIDGE_LAYER
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_fitbit_watch_plus_companion_is_multi_layer(self):
        watch_src  = 'import { HeartRateSensor } from "fitbit-sensors";\nfunction getHeartRate(){}'
        bridge_src = "import { peerSocket } from 'messaging';\nfunction getHeartRate(){}"
        f1 = _tmp(watch_src,  ".js")
        f2 = _tmp(bridge_src, ".js")
        try:
            ctx = scan_batch_for_layers([f1, f2])
            assert ctx.is_multi_layer is True
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_arduino_plus_express_api_is_multi_layer(self):
        device_src = "#include <Arduino.h>\nvoid setup(){}\nvoid loop(){ analogRead(A0); }"
        cloud_src  = "const express = require('express');\nrouter.get('/sensor', handler);"
        f1 = _tmp(device_src, ".cpp")
        f2 = _tmp(cloud_src,  ".js")
        try:
            ctx = scan_batch_for_layers([f1, f2])
            assert ctx.is_multi_layer is True
            assert ctx.layer_map[f1] == LayerType.DEVICE_LAYER
            assert ctx.layer_map[f2] == LayerType.CLOUD_LAYER
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_mqtt_device_plus_cloud_is_multi_layer(self):
        device_src = "import paho.mqtt.client as mqtt\nclient = mqtt.Client()\nclient.publish('topic', val)"
        cloud_src  = "@app.get('/data')\ndef get_data(): pass"
        f1 = _tmp(device_src, ".py")
        f2 = _tmp(cloud_src,  ".py")
        try:
            ctx = scan_batch_for_layers([f1, f2])
            assert ctx.is_multi_layer is True
        finally:
            os.unlink(f1); os.unlink(f2)


# =============================================================================
# PAIR-LEVEL CROSS-LAYER ANALYSIS
# =============================================================================

class TestCrossLayerPairAnalysis:
    def test_exact_match_device_to_bridge_kotlin(self):
        device_src = "class X : WearableListenerService() { fun getHeartRate(): Int { return 72 } }"
        bridge_src = "class Y : DataClient.OnDataChangedListener { fun getHeartRate(): Int { return 72 } }"
        f1 = _tmp(device_src, ".kt")
        f2 = _tmp(bridge_src, ".kt")
        try:
            ctx    = scan_batch_for_layers([f1, f2])
            result = analyze_cross_layer_pair(f1, f2, ctx)
            assert result is not None
            assert result.is_cross_layer is True
            assert any(m.canonical == "getHeartRate" for m in result.matches)
            assert any(m.match_type == "exact" for m in result.matches)
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_synonym_match_fetch_to_get(self):
        """fetchHeartRate() on bridge should match getHeartRate on device via synonym rule"""
        device_src  = "class X : WearableListenerService() { fun getHeartRate(): Int { return 72 } }"
        bridge_src  = "class Y : DataClient.OnDataChangedListener { fun fetchHeartRate(): Int { return 0 } }"
        f1 = _tmp(device_src, ".kt")
        f2 = _tmp(bridge_src, ".kt")
        try:
            ctx    = scan_batch_for_layers([f1, f2])
            result = analyze_cross_layer_pair(f1, f2, ctx)
            assert result is not None
            assert any(m.canonical == "getHeartRate" for m in result.matches)
            assert any(m.match_type == "synonym" for m in result.matches)
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_synonym_log_to_post(self):
        """logActivity() should normalise to postActivity — matches postActivity cloud canonical"""
        device_src = "class X : WearableListenerService() { fun logActivity(t: String) {} }"
        cloud_src  = "const express = require('express');\nrouter.post('/activity', handler);"
        f1 = _tmp(device_src, ".kt")
        f2 = _tmp(cloud_src,  ".js")
        try:
            ctx    = scan_batch_for_layers([f1, f2])
            result = analyze_cross_layer_pair(f1, f2, ctx)
            assert result is not None
            assert any(m.canonical == "postActivity" for m in result.matches)
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_rest_to_kotlin_match(self):
        """GET /heart-rate (REST) should match getHeartRate() in Kotlin via canonical form"""
        bridge_src = "class X : DataClient.OnDataChangedListener { fun getHeartRate(): Int { return 72 } }"
        cloud_src  = "GET /heart-rate\nPOST /activity/log\nGET /sleep/data"
        f1 = _tmp(bridge_src, ".kt")
        f2 = _tmp(cloud_src,  ".txt")
        try:
            ctx    = scan_batch_for_layers([f1, f2])
            result = analyze_cross_layer_pair(f1, f2, ctx)
            assert result is not None
            assert any(m.canonical == "getHeartRate" for m in result.matches), \
                f"Expected getHeartRate match. Got: {[m.canonical for m in (result.matches if result else [])]}"
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_express_routes_match_kotlin(self):
        bridge_src = (
            "class X : DataClient.OnDataChangedListener {\n"
            "  fun getHeartRate(): Int = 72\n"
            "  fun getUserProfile(id: String): Map<String,Any> = mapOf()\n"
            "}"
        )
        cloud_src = (
            "const express = require('express');\n"
            "router.get('/heart-rate', (req, res) => {});\n"
            "router.get('/user/profile', (req, res) => {});\n"
        )
        f1 = _tmp(bridge_src, ".kt")
        f2 = _tmp(cloud_src,  ".js")
        try:
            ctx    = scan_batch_for_layers([f1, f2])
            result = analyze_cross_layer_pair(f1, f2, ctx)
            assert result is not None
            canonicals = [m.canonical for m in result.matches]
            assert "getHeartRate"   in canonicals, f"Missing getHeartRate in {canonicals}"
            assert "getUserProfile" in canonicals, f"Missing getUserProfile in {canonicals}"
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_same_layer_returns_none(self):
        """Two files in the same layer — no cross-layer result expected"""
        device_a = "class X : WearableListenerService() { fun getHeartRate() {} }"
        device_b = "class Y : WearableListenerService() { fun getSleepData() {} }"
        f1 = _tmp(device_a, ".kt")
        f2 = _tmp(device_b, ".kt")
        try:
            ctx    = scan_batch_for_layers([f1, f2])
            result = analyze_cross_layer_pair(f1, f2, ctx)
            if result is not None:
                assert result.layer_a == result.layer_b or len(result.matches) == 0
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_score_proportional_to_matches(self):
        bridge_src = (
            "class X : DataClient.OnDataChangedListener {\n"
            "  fun getHeartRate(): Int = 0\n"
            "  fun getSleepData(): Map<String,Any> = mapOf()\n"
            "  fun calculateBMI(): Float = 0f\n"      # not in REST spec
            "  fun processLocally(): Unit {}\n"        # not in REST spec
            "}"
        )
        cloud_src = "GET /heart-rate\nGET /sleep/data\nGET /user/profile"
        f1 = _tmp(bridge_src, ".kt")
        f2 = _tmp(cloud_src,  ".txt")
        try:
            ctx    = scan_batch_for_layers([f1, f2])
            result = analyze_cross_layer_pair(f1, f2, ctx)
            assert result is not None
            assert 0 < result.cross_layer_score <= 1.0
        finally:
            os.unlink(f1); os.unlink(f2)

    def test_non_iot_context_returns_none(self):
        """If scan says not multi-layer, pair analysis must return None — zero cost"""
        f1 = _tmp("#include<iostream>\nint main(){return 0;}", ".cpp")
        f2 = _tmp("#include<iostream>\nvoid sort(){}", ".cpp")
        try:
            ctx    = scan_batch_for_layers([f1, f2])
            result = analyze_cross_layer_pair(f1, f2, ctx)
            assert result is None
        finally:
            os.unlink(f1); os.unlink(f2)


# =============================================================================
# SAMPLE FILE INTEGRATION TESTS
# =============================================================================

class TestSampleFiles:
    """
    End-to-end tests using the actual iot_sample/ files.
    These verify the full pipeline works on the bundled 3-tier health IoT demo.
    """

    def _skip_if_missing(self):
        for f in [DEVICE_FILE, BRIDGE_FILE, CLOUD_FILE]:
            if not f.exists():
                import pytest
                pytest.skip(f"Sample file missing: {f}")

    def test_device_file_detected_as_device_layer(self):
        self._skip_if_missing()
        src   = DEVICE_FILE.read_text()
        layer = _detect_layer_from_content(src, str(DEVICE_FILE))
        assert layer == LayerType.DEVICE_LAYER, f"Expected DEVICE_LAYER, got {layer}"

    def test_bridge_file_detected_as_bridge_layer(self):
        self._skip_if_missing()
        src   = BRIDGE_FILE.read_text()
        layer = _detect_layer_from_content(src, str(BRIDGE_FILE))
        assert layer == LayerType.BRIDGE_LAYER, f"Expected BRIDGE_LAYER, got {layer}"

    def test_cloud_file_detected_as_cloud_layer(self):
        self._skip_if_missing()
        src   = CLOUD_FILE.read_text()
        layer = _detect_layer_from_content(src, str(CLOUD_FILE))
        assert layer == LayerType.CLOUD_LAYER, f"Expected CLOUD_LAYER, got {layer}"

    def test_all_three_files_form_multi_layer_batch(self):
        self._skip_if_missing()
        ctx = scan_batch_for_layers([str(DEVICE_FILE), str(BRIDGE_FILE), str(CLOUD_FILE)])
        assert ctx.is_multi_layer is True, f"Reason: {ctx.reason}"

    def test_device_bridge_pair_has_cross_layer_matches(self):
        self._skip_if_missing()
        ctx    = scan_batch_for_layers([str(DEVICE_FILE), str(BRIDGE_FILE)])
        result = analyze_cross_layer_pair(str(DEVICE_FILE), str(BRIDGE_FILE), ctx)
        assert result is not None
        assert result.is_cross_layer is True
        canonicals = [m.canonical for m in result.matches]
        assert len(canonicals) >= 3, f"Expected ≥3 matches, got: {canonicals}"
        assert "getHeartRate"   in canonicals, f"Missing getHeartRate in {canonicals}"
        assert "getUserProfile" in canonicals, f"Missing getUserProfile in {canonicals}"

    def test_bridge_cloud_pair_has_cross_layer_matches(self):
        self._skip_if_missing()
        ctx    = scan_batch_for_layers([str(BRIDGE_FILE), str(CLOUD_FILE)])
        result = analyze_cross_layer_pair(str(BRIDGE_FILE), str(CLOUD_FILE), ctx)
        assert result is not None
        assert result.is_cross_layer is True
        canonicals = [m.canonical for m in result.matches]
        assert len(canonicals) >= 2, f"Expected ≥2 matches, got: {canonicals}"

    def test_device_cloud_pair_has_cross_layer_matches(self):
        self._skip_if_missing()
        ctx    = scan_batch_for_layers([str(DEVICE_FILE), str(CLOUD_FILE)])
        result = analyze_cross_layer_pair(str(DEVICE_FILE), str(CLOUD_FILE), ctx)
        assert result is not None
        assert result.is_cross_layer is True
        canonicals = [m.canonical for m in result.matches]
        assert len(canonicals) >= 1, f"Expected ≥1 match, got: {canonicals}"

    def test_cross_layer_scores_nonzero(self):
        self._skip_if_missing()
        ctx    = scan_batch_for_layers([str(DEVICE_FILE), str(BRIDGE_FILE)])
        result = analyze_cross_layer_pair(str(DEVICE_FILE), str(BRIDGE_FILE), ctx)
        assert result is not None
        assert result.cross_layer_score > 0, "Score should be > 0 for matched files"
        assert result.cross_layer_score <= 1.0


# =============================================================================
# QUICK CLI RUN  (also runnable as a script without pytest)
# =============================================================================

if __name__ == "__main__":
    print("Running cross-layer detection tests directly…\n")

    groups = [
        ("REST canonicalisation", TestRestToCanonical),
        ("Synonym normalisation", TestSynonymNormalisation),
        ("Layer detection",       TestLayerDetection),
        ("Batch scan",            TestBatchScan),
        ("Pair analysis",         TestCrossLayerPairAnalysis),
        ("Sample files",          TestSampleFiles),
    ]

    passed = failed = skipped = 0

    for group_name, cls in groups:
        instance = cls()
        for attr in dir(instance):
            if not attr.startswith("test_"):
                continue
            fn = getattr(instance, attr)
            label = f"{group_name} / {attr}"
            try:
                fn()
                print(f"  ✅  {label}")
                passed += 1
            except AssertionError as e:
                print(f"  ❌  {label}  →  {e}")
                failed += 1
            except Exception as e:
                # pytest.skip raises a special exception — treat as skipped
                if "skip" in type(e).__name__.lower():
                    print(f"  ⏭️   {label}  →  skipped")
                    skipped += 1
                else:
                    print(f"  💥  {label}  →  {type(e).__name__}: {e}")
                    failed += 1

    total = passed + failed + skipped
    print(f"\n{passed}/{total} passed  ({skipped} skipped)")
    if failed:
        print(f"⚠️  {failed} test(s) failed")
