# detectors/type4/type4_detector.py
"""
Type-4 Detector — unified adapter for engine/analyzer.py

Wraps JoernDetector (primary) with custom_pdg fallback.
Provides the interface that engine/analyzer.py expects:

    detect(file_a, file_b, include_features=False)
    → {
        "semantic_score": float,
        "is_semantic_clone": bool,
        "confidence": str,           # HIGH / MEDIUM / LOW / UNLIKELY
        "category_scores": {
            "control_flow": float,
            "data_flow": float,
            "call_pattern": float,
            "structural": float,
            "behavioral": float,
        },
        "features_a": {"behavioral_hash": str, ...},
        "features_b": {"behavioral_hash": str, ...},
      }

    prepare_batch(file_paths) — no-op (kept for API compatibility)
    clear_cache()             — no-op (kept for API compatibility)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Extension → language for Joern
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
    ".go":   "go",
    ".php":  "php",
}


class Type4Detector:
    """
    Unified Type-4 semantic clone detector.

    Tries Joern first; falls back to custom_pdg if Joern / Docker
    is unavailable.
    """

    def __init__(self, threshold: float = 0.55):
        self.threshold = threshold
        self._joern: Any   = None
        self._custom: Any  = None
        self._mode: str    = "uninitialized"
        self._init_backend()

    # ─── backend initialization ────────────────────────────────────────

    def _init_backend(self) -> None:
        """Try to load Joern; fall back to custom_pdg."""
        try:
            from detectors.type4.joern.joern_detector import JoernDetector
            detector = JoernDetector(auto_start=True)
            # Quick sanity — did Docker come up?
            status = detector.get_status()
            if status.get("docker_available") and status.get("container_running"):
                self._joern = detector
                self._mode  = "joern"
                logger.info("✅ [Type4] Using Joern PDG backend")
                return
            else:
                logger.warning("⚠️  [Type4] Joern container not running — falling back")
        except Exception as e:
            logger.warning(f"⚠️  [Type4] Joern init failed ({e}) — falling back to custom_pdg")

        # Fallback
        try:
            from detectors.type4.custom_pdg.pdg_detector import Type4PDGDetector
            self._custom = Type4PDGDetector(threshold=self.threshold)
            self._mode   = "custom_pdg"
            logger.info("✅ [Type4] Using custom PDG backend (fallback)")
        except Exception as e:
            logger.error(f"❌ [Type4] Both backends failed: {e}")
            self._mode = "unavailable"

    # ─── public API used by engine/analyzer.py ─────────────────────────

    def detect(
        self,
        file_a: "str | Path",
        file_b: "str | Path",
        include_features: bool = False,
    ) -> Dict[str, Any]:
        """Detect semantic similarity between two files."""

        fa, fb = str(file_a), str(file_b)

        if self._mode == "joern":
            return self._detect_joern(fa, fb, include_features)
        elif self._mode == "custom_pdg":
            return self._detect_custom(fa, fb, include_features)
        else:
            return self._unavailable_result()

    def prepare_batch(self, file_paths: List[Any]) -> None:
        """No-op — kept for API compatibility with Type3 detector."""
        pass

    def clear_cache(self) -> None:
        """No-op — kept for API compatibility."""
        pass

    # ─── Joern path ────────────────────────────────────────────────────

    def _detect_joern(
        self,
        fa: str,
        fb: str,
        include_features: bool,
    ) -> Dict[str, Any]:
        try:
            result = self._joern.detect_from_files(fa, fb)

            if result.status == "error":
                logger.warning(f"[Type4/Joern] error: {result.error_message}")
                return self._error_result(result.error_message)

            scores = result.scores

            # Map ConfidenceLevel enum → string used by analyzer
            conf_map = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}
            confidence = conf_map.get(
                result.confidence.value if result.confidence else "low",
                "LOW"
            )
            if result.similarity < self.threshold * 0.7:
                confidence = "UNLIKELY"

            out = {
                "semantic_score":    round(result.similarity, 4),
                "is_semantic_clone": result.is_semantic_clone,
                "confidence":        confidence,
                "backend":           "joern",
                "category_scores": {
                    "control_flow": round(scores.control_flow_similarity, 4),
                    "data_flow":    round(scores.data_flow_similarity,    4),
                    "call_pattern": round(scores.node_type_similarity,    4),
                    "structural":   round(scores.structural_similarity,   4),
                    "behavioral":   round(
                        (scores.control_flow_similarity + scores.data_flow_similarity) / 2,
                        4
                    ),
                },
            }

            if include_features:
                # Attach PDG info as proxy for features
                out["features_a"] = {
                    "behavioral_hash": f"pdg:{result.pdg1_info.num_nodes}n:{result.pdg1_info.num_edges}e",
                    "num_nodes":       result.pdg1_info.num_nodes,
                    "num_edges":       result.pdg1_info.num_edges,
                    "methods":         result.pdg1_info.method_names,
                }
                out["features_b"] = {
                    "behavioral_hash": f"pdg:{result.pdg2_info.num_nodes}n:{result.pdg2_info.num_edges}e",
                    "num_nodes":       result.pdg2_info.num_nodes,
                    "num_edges":       result.pdg2_info.num_edges,
                    "methods":         result.pdg2_info.method_names,
                }

            return out

        except Exception as e:
            logger.error(f"[Type4/Joern] detect_from_files crashed: {e}")
            # Try custom_pdg as emergency fallback
            if self._custom:
                return self._detect_custom(fa, fb, include_features)
            return self._error_result(str(e))

    # ─── custom_pdg path ───────────────────────────────────────────────

    def _detect_custom(
        self,
        fa: str,
        fb: str,
        include_features: bool,
    ) -> Dict[str, Any]:
        try:
            raw = self._custom.detect(fa, fb, include_features=include_features)
            # custom_pdg already returns the right dict format
            raw["backend"] = "custom_pdg"
            return raw
        except Exception as e:
            logger.error(f"[Type4/custom_pdg] crashed: {e}")
            return self._error_result(str(e))

    # ─── helpers ───────────────────────────────────────────────────────

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