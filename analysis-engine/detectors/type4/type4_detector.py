# detectors/type4/type4_detector.py
"""
Type-4 Detector — unified adapter for engine/analyzer.py

Architecture:
  Primary:  EducationalType4Detector
              │
              ├── AlgorithmClassifier   (static signature, problem category)
              ├── IOBehavioralTester    (compile + run with harness, compare outputs)
              └── JoernDetector         (PDG WL-kernel, if Docker available)

  Fallback: If EducationalType4Detector fails to initialize (no g++, etc.),
            falls back to the legacy custom_pdg detector.

Public interface (used by engine/analyzer.py):
    detector.detect(file_a, file_b, include_features=False)
    → {
        "semantic_score":    float,
        "is_semantic_clone": bool,
        "confidence":        str,
        "backend":           str,
        "category_scores":   {...},
        ...
      }
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Extension → language
_EXT_LANG: Dict[str, str] = {
    ".py":   "python",
    ".java": "java",
    ".js":   "javascript",
    ".jsx":  "javascript",
    ".ts":   "javascript",
    ".tsx":  "javascript",
    ".c":    "c",
    ".cpp":  "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".h":    "cpp", ".hpp": "cpp",
}


class Type4Detector:
    """
    Unified Type-4 semantic clone detector with educational pipeline.

    Init order:
      1. Try EducationalType4Detector (our custom pipeline).
      2. If educational detector is ready but Joern is also available,
         the educational detector automatically gets the Joern PDG signal.
      3. If educational detector cannot init, fall back to custom_pdg.
      4. If custom_pdg also fails, the detector is "unavailable" and
         all detections return zero scores.
    """

    def __init__(self, threshold: float = 0.60) -> None:
        self.threshold = threshold
        self._edu:     Any = None
        self._custom:  Any = None
        self._joern:   Any = None
        self._mode:    str = "uninitialized"
        self._init_backend()

    # ─── initialization ───────────────────────────────────────────────────────

    def _init_backend(self) -> None:
        """
        Try to initialize the educational detector.
        Falls back to custom_pdg if anything critical fails.
        """
        logger.info("[Type4Detector] Initializing backend…")

        # ── Step 1: try to load Joern (optional — educational works without it) ──
        joern_detector = self._try_load_joern()

        # ── Step 2: load the educational detector ─────────────────────────────
        try:
            from detectors.type4.educational import EducationalType4Detector

            # Check g++ is available (needed for C++ I/O testing)
            g_plus_plus = shutil.which("g++")
            if not g_plus_plus:
                logger.warning(
                    "[Type4Detector] g++ not found on PATH — "
                    "I/O testing for C++ will be disabled"
                )

            self._edu = EducationalType4Detector(
                joern_detector  = joern_detector,
                io_threshold    = self.threshold,
                enable_io       = True,
                enable_joern    = joern_detector is not None,
            )
            self._mode = "educational"
            logger.info(
                "✅ [Type4Detector] Using EDUCATIONAL pipeline "
                "(joern=%s, io_testing=%s)",
                joern_detector is not None,
                g_plus_plus is not None,
            )
            return

        except ImportError as exc:
            logger.warning("[Type4Detector] Educational module import failed: %s", exc)
        except Exception as exc:
            logger.warning("[Type4Detector] Educational detector init error: %s", exc)

        # ── Step 3: fall back to custom_pdg ───────────────────────────────────
        try:
            from detectors.type4.custom_pdg.pdg_detector import Type4PDGDetector
            self._custom = Type4PDGDetector(threshold=self.threshold)
            self._mode   = "custom_pdg"
            logger.info("⚠️  [Type4Detector] Fallback: using custom_pdg backend")
            return
        except Exception as exc:
            logger.error("[Type4Detector] custom_pdg fallback failed: %s", exc)

        # ── Step 4: unavailable ────────────────────────────────────────────────
        self._mode = "unavailable"
        logger.error("❌ [Type4Detector] All backends failed — Type-4 will return zeros")

    def _try_load_joern(self) -> Optional[Any]:
        """
        Attempt to load JoernDetector. Returns instance or None (never raises).
        """
        try:
            from detectors.type4.joern.joern_detector import JoernDetector
            detector = JoernDetector(auto_start=True)
            status   = detector.get_status()
            if status.get("docker_available") and status.get("container_running"):
                self._joern = detector
                logger.info("✅ [Type4Detector] Joern container is running")
                return detector
            else:
                logger.info(
                    "[Type4Detector] Joern container not running "
                    "(docker=%s running=%s) — PDG signal will be skipped",
                    status.get("docker_available"),
                    status.get("container_running"),
                )
                return None
        except Exception as exc:
            logger.info("[Type4Detector] Joern not available: %s", exc)
            return None

    # ─── public API ───────────────────────────────────────────────────────────

    def detect(
        self,
        file_a: "str | Path",
        file_b: "str | Path",
        include_features: bool = False,
    ) -> Dict[str, Any]:
        """
        Detect Type-4 semantic similarity between two source files.

        Args:
            file_a:           Path to first source file.
            file_b:           Path to second source file.
            include_features: If True, attach diagnostic details to result.

        Returns:
            Detection result dict. Never raises.
        """
        fa, fb = str(file_a), str(file_b)
        logger.debug(
            "[Type4Detector] detect(%s, %s) mode=%s",
            Path(fa).name, Path(fb).name, self._mode,
        )

        if self._mode == "educational":
            return self._detect_educational(fa, fb, include_features)
        elif self._mode == "custom_pdg":
            return self._detect_custom(fa, fb, include_features)
        else:
            return self._unavailable_result()

    def prepare_batch(self, file_paths: List[Any]) -> None:
        """No-op — kept for API compatibility."""
        pass

    def clear_cache(self) -> None:
        """No-op — kept for API compatibility."""
        pass

    def get_mode(self) -> str:
        """Return the active backend mode string."""
        return self._mode

    # ─── dispatch helpers ─────────────────────────────────────────────────────

    def _detect_educational(
        self, fa: str, fb: str, include_features: bool
    ) -> Dict[str, Any]:
        try:
            result = self._edu.detect(fa, fb, include_features=include_features)
            result["backend"] = "educational_type4"
            return result
        except Exception as exc:
            logger.error("[Type4Detector] Educational detect() error: %s", exc)
            # Try custom_pdg as emergency fallback
            if self._custom:
                logger.info("[Type4Detector] Emergency fallback to custom_pdg")
                return self._detect_custom(fa, fb, include_features)
            return self._error_result(str(exc))

    def _detect_custom(
        self, fa: str, fb: str, include_features: bool
    ) -> Dict[str, Any]:
        try:
            raw = self._custom.detect(fa, fb, include_features=include_features)
            raw["backend"] = "custom_pdg"
            return raw
        except Exception as exc:
            logger.error("[Type4Detector] custom_pdg detect() error: %s", exc)
            return self._error_result(str(exc))

    # ─── static result builders ───────────────────────────────────────────────

    @staticmethod
    def _unavailable_result() -> Dict[str, Any]:
        return {
            "semantic_score":    0.0,
            "is_semantic_clone": False,
            "confidence":        "UNLIKELY",
            "backend":           "unavailable",
            "category_scores":   {
                "control_flow": 0.0,
                "data_flow":    0.0,
                "call_pattern": 0.0,
                "structural":   0.0,
                "behavioral":   0.0,
            },
        }

    @staticmethod
    def _error_result(msg: str) -> Dict[str, Any]:
        result = Type4Detector._unavailable_result()
        result["error"] = msg
        return result
