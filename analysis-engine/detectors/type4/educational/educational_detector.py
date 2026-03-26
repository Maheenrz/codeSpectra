# detectors/type4/educational/educational_detector.py
"""
Educational Type-4 Detector — top-level orchestrator.

Combines three signals for educational-context semantic clone detection:
  1. PDG WL-kernel similarity (from Joern)
  2. I/O behavioral testing (from IOBehavioralTester)
  3. Algorithm signature (from AlgorithmClassifier)

Pipeline:
  for each (file_a, file_b):
    a. AlgorithmClassifier    → category, algorithm_family_a/b
    b. IOBehavioralTester     → io_match_score, mutual_correctness
    c. JoernDetector          → pdg_score (if available; else 0.0)
    d. ScoreFusion            → final_score, confidence, is_semantic_clone

The detector is designed to NEVER raise. All failures are caught, logged,
and return safe fallback results.

Public interface (matches what engine/analyzer.py calls):
    detector.detect(file_a, file_b, include_features=False)
    → {
        "semantic_score":    float,
        "is_semantic_clone": bool,
        "confidence":        str,  # "HIGH"/"MEDIUM"/"LOW"/"UNLIKELY"
        "backend":           str,
        "category_scores":   {...},
        "io_match_score":    float | None,
        "io_available":      bool,
        "interpretation":    str,
      }
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .algorithm_classifier import get_classifier, ClassificationResult
from .io_behavioral_tester import get_tester, IOBehavioralResult
from .score_fusion import FusionInput, FusionResult, fuse_scores

logger = logging.getLogger(__name__)


# ─── Language extension map (for Joern language lookup) ──────────────────────

_EXT_LANG: Dict[str, str] = {
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".c": "cpp",
    ".java": "java",
    ".py": "python",
    ".js": "javascript",
}


class EducationalType4Detector:
    """
    Complete educational Type-4 semantic clone detector.

    Args:
        joern_detector: Optional JoernDetector instance. If None, PDG signal
                        is skipped (I/O + signature still run).
        io_threshold:   Minimum final score to declare is_semantic_clone.
        max_test_cases: Cap on test cases per run (controls latency).
        enable_io:      Toggle I/O behavioral testing on/off.
        enable_joern:   Toggle PDG analysis on/off.
    """

    def __init__(
        self,
        joern_detector=None,
        io_threshold:   float = 0.60,
        max_test_cases: int   = 15,
        enable_io:      bool  = True,
        enable_joern:   bool  = True,
    ) -> None:
        self._joern          = joern_detector
        self._threshold      = io_threshold
        self._enable_io      = enable_io
        self._enable_joern   = enable_joern and joern_detector is not None
        self._classifier     = get_classifier()
        self._io_tester      = get_tester()

        logger.info(
            "[EduDetector] Initialized | joern=%s io=%s threshold=%.2f",
            self._enable_joern, self._enable_io, self._threshold,
        )

    # ─── public API ──────────────────────────────────────────────────────────

    def detect(
        self,
        file_a: str,
        file_b: str,
        include_features: bool = False,
    ) -> Dict[str, Any]:
        """
        Run the full three-signal Type-4 detection pipeline.

        Args:
            file_a:           Absolute path to student A's source.
            file_b:           Absolute path to student B's source.
            include_features: If True, attach extra diagnostic info.

        Returns:
            Detection result dict (engine-compatible shape).
            Never raises — on any error returns a zero-score fallback dict.
        """
        t_start = time.time()
        name_a  = Path(file_a).name
        name_b  = Path(file_b).name
        logger.info("[EduDetector] Detecting: %s  vs  %s", name_a, name_b)

        try:
            return self._detect_inner(file_a, file_b, include_features, t_start)
        except Exception as exc:
            logger.exception("[EduDetector] Unhandled exception: %s", exc)
            return self._fallback_result(str(exc))

    def prepare_batch(self, file_paths: List[Any]) -> None:
        """No-op — kept for API compatibility."""
        pass

    def clear_cache(self) -> None:
        """No-op — kept for API compatibility."""
        pass

    # ─── internal pipeline ───────────────────────────────────────────────────

    def _detect_inner(
        self,
        file_a:           str,
        file_b:           str,
        include_features: bool,
        t_start:          float,
    ) -> Dict[str, Any]:

        fusion_input = FusionInput()

        # ── Signal 1: Algorithm Classifier ───────────────────────────────
        logger.debug("[EduDetector] Running algorithm classifier…")
        cls_a = self._classifier.classify_file(file_a)
        cls_b = self._classifier.classify_file(file_b)

        fusion_input.algorithm_a = cls_a.algorithm_family
        fusion_input.algorithm_b = cls_b.algorithm_family
        fusion_input.category    = cls_a.category if cls_a.category == cls_b.category else ""
        fusion_input.language    = _EXT_LANG.get(Path(file_a).suffix.lower(), "")

        if cls_a.category and cls_b.category:
            fusion_input.same_algo_family = (
                cls_a.algorithm_family == cls_b.algorithm_family
                and bool(cls_a.algorithm_family)
            )
        else:
            fusion_input.same_algo_family = None   # unknown

        logger.debug(
            "[EduDetector] Classifier: A=%s B=%s same=%s",
            cls_a, cls_b, fusion_input.same_algo_family,
        )

        # ── Signal 2: I/O Behavioral Testing ─────────────────────────────
        io_result: Optional[IOBehavioralResult] = None

        if self._enable_io:
            logger.debug("[EduDetector] Running I/O behavioral tests…")
            io_result = self._io_tester.test(file_a, file_b)
            logger.debug("[EduDetector] I/O result: %s", io_result)

            if io_result.succeeded and io_result.io_match_score is not None:
                fusion_input.io_match_score     = io_result.io_match_score
                fusion_input.mutual_correctness = io_result.mutual_correctness
                # If same category detected by I/O tester, prefer its category
                if io_result.category:
                    fusion_input.category = io_result.category
                # Reconcile same_algo_family with I/O result
                if io_result.same_algorithm_family and fusion_input.same_algo_family is None:
                    fusion_input.same_algo_family = io_result.same_algorithm_family
            else:
                reason = io_result.error_message or "no output"
                logger.info("[EduDetector] I/O testing skipped/failed: %s", reason)
        else:
            logger.debug("[EduDetector] I/O testing disabled")

        # ── Signal 3: PDG WL Kernel (Joern) ──────────────────────────────
        if self._enable_joern and self._joern is not None:
            logger.debug("[EduDetector] Running Joern PDG analysis…")
            try:
                joern_result = self._joern.detect_from_files(file_a, file_b)
                if joern_result.status == "success":
                    fusion_input.pdg_score = joern_result.similarity
                    logger.debug(
                        "[EduDetector] Joern PDG similarity: %.3f",
                        joern_result.similarity,
                    )
                else:
                    logger.info(
                        "[EduDetector] Joern returned non-success: %s",
                        joern_result.error_message,
                    )
            except Exception as exc:
                logger.warning("[EduDetector] Joern exception (non-fatal): %s", exc)
        else:
            logger.debug("[EduDetector] Joern PDG disabled or unavailable")

        # ── Signal Fusion ─────────────────────────────────────────────────
        logger.debug("[EduDetector] Fusing scores…")
        fusion = fuse_scores(fusion_input, threshold=self._threshold)

        elapsed_ms = round((time.time() - t_start) * 1000, 2)
        logger.info(
            "[EduDetector] Done in %dms: final=%.3f confidence=%s clone=%s",
            elapsed_ms, fusion.final_score, fusion.confidence, fusion.is_semantic_clone,
        )

        # ── Build result dict ─────────────────────────────────────────────
        out = fusion.to_detector_dict()
        out["analysis_time_ms"] = elapsed_ms

        if include_features:
            out["diagnostic"] = {
                "classifier_a":     {
                    "category":   cls_a.category,
                    "family":     cls_a.algorithm_family,
                    "confidence": cls_a.confidence,
                    "is_oop":     cls_a.is_oop,
                },
                "classifier_b":     {
                    "category":   cls_b.category,
                    "family":     cls_b.algorithm_family,
                    "confidence": cls_b.confidence,
                    "is_oop":     cls_b.is_oop,
                },
                "io_result":        self._io_result_summary(io_result),
                "fusion_input":     {
                    "pdg_score":        fusion_input.pdg_score,
                    "io_match_score":   fusion_input.io_match_score,
                    "mutual_correct":   fusion_input.mutual_correctness,
                    "same_algo_family": fusion_input.same_algo_family,
                    "category":         fusion_input.category,
                },
                "pdg_contribution":  fusion.pdg_contribution,
                "io_contribution":   fusion.io_contribution,
                "sig_contribution":  fusion.sig_contribution,
            }

        return out

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _io_result_summary(io_result: Optional[IOBehavioralResult]) -> Dict[str, Any]:
        if io_result is None:
            return {"ran": False}
        return {
            "ran":               io_result.succeeded,
            "category":          io_result.category,
            "total_cases":       io_result.total_cases,
            "runnable_cases":    io_result.runnable_cases,
            "matched_cases":     io_result.matched_cases,
            "io_match_score":    io_result.io_match_score,
            "mutual_correct":    io_result.mutual_correctness,
            "same_algo_family":  io_result.same_algorithm_family,
            "error_message":     io_result.error_message or None,
        }

    @staticmethod
    def _fallback_result(error_msg: str = "") -> Dict[str, Any]:
        return {
            "semantic_score":    0.0,
            "is_semantic_clone": False,
            "confidence":        "UNLIKELY",
            "backend":           "educational_type4",
            "category_scores":   {
                "control_flow": 0.0,
                "data_flow":    0.0,
                "call_pattern": 0.0,
                "structural":   0.0,
                "behavioral":   0.0,
            },
            "io_match_score":  None,
            "io_available":    False,
            "interpretation":  f"Detection failed: {error_msg}" if error_msg else "Detection failed",
        }
