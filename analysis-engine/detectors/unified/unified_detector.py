# analysis-engine/detectors/unified/unified_detector.py

"""
Unified Clone Detection Engine — v2.2
======================================

v2.2 adds: Cross-Layer / IoT awareness
  - detect_batch() now scans the whole file set ONCE for layer signals
  - detect() accepts an optional layer_context so the batch scan isn't repeated per pair
  - UnifiedResult carries a cross_layer field (None when not applicable)
  - CloneType and stats both include CROSS_LAYER
  - Zero cost for regular student assignment batches (gated by is_multi_layer flag)

v2.1 fixes:
  1. _process_type3_result uses OR logic for combined score (not AND)
  2. If ML unavailable, uses hybrid score alone
  3. _determine_clone_type now uses type1/type2 scores too
  4. to_dict includes type1_score and type2_score
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import time
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from detectors.type1.type1_detector import Type1Detector
from detectors.type2.type2_detector import Type2Detector
from detectors.type3.hybrid_detector import Type3HybridDetector
from detectors.type4.type4_detector import Type4Detector

# Cross-layer module — imported lazily so a missing dep never breaks regular flow
try:
    from utils.iot_layer_detector import (
        scan_batch_for_layers,
        analyze_cross_layer_pair,
        LayerContext,
        CrossLayerResult,
    )
    _CROSS_LAYER_AVAILABLE = True
except ImportError:
    _CROSS_LAYER_AVAILABLE = False


# =============================================================================
# ENUMS
# =============================================================================

class CloneType(Enum):
    """Primary clone type detected — CROSS_LAYER added in v2.2"""
    TYPE1         = "TYPE1"
    TYPE2         = "TYPE2"
    TYPE3         = "TYPE3"
    TYPE4         = "TYPE4"
    TYPE3_AND_TYPE4 = "TYPE3_AND_TYPE4"
    CROSS_LAYER   = "CROSS_LAYER"   # same feature found across architectural layers
    NONE          = "NONE"


class RiskLevel(Enum):
    """Risk level for plagiarism"""
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MEDIUM   = "MEDIUM"
    LOW      = "LOW"
    NONE     = "NONE"


class ReviewAction(Enum):
    """Recommended action for teacher"""
    IMMEDIATE_REVIEW = "IMMEDIATE_REVIEW"
    SCHEDULED_REVIEW = "SCHEDULED_REVIEW"
    MANUAL_CHECK     = "MANUAL_CHECK"
    NOTE_ONLY        = "NOTE_ONLY"
    NO_ACTION        = "NO_ACTION"


# =============================================================================
# CONFIGURATION
# =============================================================================

THRESHOLDS = {
    'type3': {
        'clone':    0.50,
        'high':     0.70,
        'critical': 0.85,
    },
    'type4': {
        'clone':    0.60,
        'high':     0.80,
        'critical': 0.90,
    },
    'teacher_review': 0.70,
    # A cross-layer score >= this is worth flagging for the teacher
    'cross_layer_review': 0.30,
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Type3Result:
    """Type-3 detection result (shown separately)"""
    score:      float
    is_clone:   bool
    confidence: str
    details:    Dict[str, Any] = field(default_factory=dict)


@dataclass
class Type4Result:
    """Type-4 detection result (shown separately)"""
    score:           float
    is_clone:        bool
    confidence:      str
    category_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class UnifiedResult:
    """
    Complete unified detection result — v2.2 adds cross_layer field.
    cross_layer is None for any pair where IoT/multi-layer detection
    is not applicable (the common case for student assignments).
    """
    file_a: str
    file_b: str

    # Separate per-type results
    type3: Type3Result
    type4: Type4Result

    # Combined verdict
    clone_type:    str
    risk_level:    str
    combined_score: float

    # Teacher guidance
    needs_teacher_review: bool
    review_action:        str
    explanation:          str

    # Individual type1/type2 scores
    type1_score:        float = 0.0
    type2_score:        float = 0.0
    primary_clone_type: str   = "none"

    # v2.2 — cross-layer result, None when not applicable
    cross_layer: Optional[Any] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON response"""
        d = {
            "file_a": self.file_a,
            "file_b": self.file_b,

            "type1_score":        self.type1_score,
            "type2_score":        self.type2_score,
            "primary_clone_type": self.primary_clone_type,

            # Type-3 and Type-4 results (kept separate for the frontend tabs)
            "type3": {
                "score":      self.type3.score,
                "is_clone":   self.type3.is_clone,
                "confidence": self.type3.confidence,
                "details":    self.type3.details,
            },
            "type4": {
                "score":           self.type4.score,
                "is_clone":        self.type4.is_clone,
                "confidence":      self.type4.confidence,
                "category_scores": self.type4.category_scores,
            },

            # Combined verdict block read by the frontend summary card
            "verdict": {
                "clone_type":           self.clone_type,
                "risk_level":           self.risk_level,
                "combined_score":       self.combined_score,
                "needs_teacher_review": self.needs_teacher_review,
                "review_action":        self.review_action,
                "explanation":          self.explanation,
            },

            # Flat aliases used by parts of the frontend that predate the nested structure
            "structural": {
                "score":      self.type3.score,
                "confidence": self.type3.confidence,
                "is_similar": self.type3.is_clone,
            },
            "semantic": {
                "score":      self.type4.score,
                "confidence": self.type4.confidence,
                "is_similar": self.type4.is_clone,
            },

            # v2.2 — cross-layer block; null in JSON when not applicable
            "cross_layer": self.cross_layer.to_dict() if self.cross_layer else None,
        }
        return d


# =============================================================================
# UNIFIED DETECTOR
# =============================================================================

class UnifiedDetector:
    """
    Unified Clone Detection Engine — runs all detection types in one pass.

    Usage:
        detector = UnifiedDetector()

        # Single pair (no layer context — cross-layer detection skipped)
        result = detector.detect("file1.cpp", "file2.cpp")

        # Batch — layer scan runs once, cross-layer detection fires automatically
        results = detector.detect_batch(["watch.js", "companion.js", "endpoints.txt"])
    """

    def __init__(
        self,
        type3_hybrid_threshold: float = 0.50,
        type3_ml_threshold:     float = 0.60,
        type4_threshold:        float = 0.60,
        teacher_review_threshold: float = 0.70,
    ):
        self.type1_detector = Type1Detector()
        self.type2_detector = Type2Detector()
        self.type3_detector = Type3HybridDetector(
            hybrid_threshold=type3_hybrid_threshold,
            ml_threshold=type3_ml_threshold,
        )
        self.type4_detector = Type4Detector(threshold=type4_threshold)
        self.teacher_review_threshold = teacher_review_threshold
        cross_layer_status = "enabled" if _CROSS_LAYER_AVAILABLE else "unavailable (iot_layer_detector not found)"
        print(f"✅ Unified Detector Initialized (Type 1–4, cross-layer: {cross_layer_status})")

    # =========================================================================
    # CROSS-LAYER CONTEXT — scanned once per batch, not per pair
    # =========================================================================

    def _get_layer_context(self, file_paths: List[str]):
        """
        Run the IoT layer scan across all files in the batch exactly once.
        Returns a LayerContext with is_multi_layer=False for regular student
        assignments — meaning no cross-layer overhead at all for those cases.
        """
        if not _CROSS_LAYER_AVAILABLE:
            return None
        return scan_batch_for_layers(file_paths)

    # =========================================================================
    # MAIN DETECTION METHODS
    # =========================================================================

    def detect(
        self,
        file_path_a:   str,
        file_path_b:   str,
        layer_context = None,   # pass in the pre-scanned context from detect_batch()
    ) -> "UnifiedResult":
        """
        Analyse a single file pair with all four detectors plus optional
        cross-layer matching. If layer_context is None (e.g. called directly
        without a batch scan), cross-layer detection is skipped.
        """
        file_a = Path(file_path_a)
        file_b = Path(file_path_b)

        # Run all four traditional detectors
        type1_raw = self.type1_detector.detect(str(file_a), str(file_b))
        type2_raw = self.type2_detector.detect(str(file_a), str(file_b))
        type3_raw = self.type3_detector.detect(file_a, file_b)
        type4_raw = self.type4_detector.detect(str(file_a), str(file_b))

        type3_result = self._process_type3_result(type3_raw)
        type4_result = self._process_type4_result(type4_raw)

        type1_score = type1_raw.get("type1_score", 0.0)
        type2_score = type2_raw.get("type2_score", 0.0)

        # v2.2 — run cross-layer analysis if we have batch context.
        # This is always None when called standalone (e.g. from the comparison route).
        cross_layer_result = None
        if layer_context is not None and _CROSS_LAYER_AVAILABLE:
            try:
                cross_layer_result = analyze_cross_layer_pair(
                    str(file_a), str(file_b), layer_context
                )
            except Exception as e:
                print(f"⚠️ [UnifiedDetector] Cross-layer check failed ({file_a.name} vs {file_b.name}): {e}")

        primary_clone_type = self._determine_primary_clone_type(
            type1_score, type2_score, type3_result.score, type4_result.score,
            cross_layer_result,
        )

        clone_type     = self._determine_clone_type(type3_result, type4_result, cross_layer_result)
        risk_level     = self._determine_risk_level(type3_result, type4_result, cross_layer_result)
        combined_score = (
            type1_score         * 0.10 +
            type2_score         * 0.15 +
            type3_result.score  * 0.45 +
            type4_result.score  * 0.30
        )

        needs_review  = combined_score >= self.teacher_review_threshold
        # Cross-layer matches with enough shared functions are also review-worthy
        if cross_layer_result and cross_layer_result.cross_layer_score >= THRESHOLDS['cross_layer_review']:
            needs_review = True

        review_action = self._determine_review_action(risk_level)
        explanation   = self._generate_explanation(
            type3_result, type4_result, clone_type, primary_clone_type, cross_layer_result
        )

        return UnifiedResult(
            file_a=file_a.name,
            file_b=file_b.name,
            type3=type3_result,
            type4=type4_result,
            clone_type=clone_type.value,
            risk_level=risk_level.value,
            combined_score=round(combined_score, 4),
            needs_teacher_review=needs_review,
            review_action=review_action.value,
            explanation=explanation,
            type1_score=round(type1_score, 4),
            type2_score=round(type2_score, 4),
            primary_clone_type=primary_clone_type,
            cross_layer=cross_layer_result,
        )

    def detect_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyse all pairs in a file set. Scans for IoT layers once up front,
        then passes the context to every detect() call for free cross-layer detection.
        Also runs cross-language pairs when a multi-layer codebase is detected
        (e.g. JS watch file paired with a REST spec file that share method names).
        """
        from engine.analyzer import build_same_language_pairs, _build_all_pairs

        start_time = time.time()
        n = len(file_paths)

        # One-time batch scan — decides whether cross-layer logic fires at all
        layer_context = self._get_layer_context(file_paths)
        if layer_context and layer_context.is_multi_layer:
            print(f"🌐 [UnifiedDetector] Cross-layer codebase detected: {layer_context.reason}")

        same_lang_pairs   = build_same_language_pairs(file_paths)
        total_comparisons = len(same_lang_pairs)

        print(f"🔍 Comparing {n} files → {total_comparisons} same-language pairs...")

        self.type3_detector.prepare_batch([Path(p) for p in file_paths])
        self.type4_detector.clear_cache()

        results: List[UnifiedResult] = []

        # Standard same-language pairs — the normal student assignment path
        for file_a, file_b in same_lang_pairs:
            result = self.detect(file_a, file_b, layer_context=layer_context)
            results.append(result)

        # Cross-language pairs — only relevant for IoT / multi-tier repos
        if layer_context and layer_context.is_multi_layer and _CROSS_LAYER_AVAILABLE:
            same_lang_set = set(same_lang_pairs)
            for file_a, file_b in _build_all_pairs(file_paths):
                if (file_a, file_b) in same_lang_set:
                    continue
                cl = analyze_cross_layer_pair(file_a, file_b, layer_context)
                if cl and cl.matches:
                    # For cross-language pairs the traditional detectors are meaningless,
                    # so we emit a stub result with only the cross_layer payload filled in.
                    results.append(self._make_cross_layer_stub(file_a, file_b, cl))

        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'NONE': 4}
        results.sort(key=lambda x: (risk_order.get(x.risk_level, 5), -x.combined_score))

        stats           = self._calculate_batch_stats(results)
        teacher_summary = self._generate_teacher_summary(results, stats)

        processing_time = (time.time() - start_time) * 1000

        return {
            "total_files":        n,
            "total_comparisons":  total_comparisons,
            "processing_time_ms": round(processing_time, 2),
            "statistics":         stats,
            "teacher_summary":    teacher_summary,
            "results":            [r.to_dict() for r in results],
        }

    # =========================================================================
    # STUB BUILDER — for cross-language pairs that only have cross-layer data
    # =========================================================================

    def _make_cross_layer_stub(self, file_a: str, file_b: str, cl_result) -> "UnifiedResult":
        """
        Wraps a cross-layer-only result in a UnifiedResult so it can travel
        through the same pipeline as everything else. The Type1-4 scores are all
        zero because those detectors don't operate across languages.
        """
        empty_type3 = Type3Result(score=0.0, is_clone=False, confidence="UNLIKELY")
        empty_type4 = Type4Result(score=0.0, is_clone=False, confidence="UNLIKELY")

        needs_review = cl_result.cross_layer_score >= THRESHOLDS['cross_layer_review']
        explanation  = cl_result.explanation

        return UnifiedResult(
            file_a=Path(file_a).name,
            file_b=Path(file_b).name,
            type3=empty_type3,
            type4=empty_type4,
            clone_type=CloneType.CROSS_LAYER.value,
            risk_level=RiskLevel.MEDIUM.value if needs_review else RiskLevel.LOW.value,
            combined_score=round(cl_result.cross_layer_score, 4),
            needs_teacher_review=needs_review,
            review_action=ReviewAction.MANUAL_CHECK.value if needs_review else ReviewAction.NOTE_ONLY.value,
            explanation=explanation,
            primary_clone_type="cross_layer",
            cross_layer=cl_result,
        )

    # =========================================================================
    # RESULT PROCESSING
    # =========================================================================

    def _process_type3_result(self, raw: Dict) -> Type3Result:
        """Process raw Type-3 detector output. Uses hybrid score alone if ML unavailable."""
        hybrid      = raw["hybrid"]
        ml          = raw.get("ml")
        hybrid_score = hybrid["score"]
        ml_score     = ml["score"] if ml else None

        combined    = (hybrid_score * 0.6 + ml_score * 0.4) if ml_score is not None else hybrid_score
        is_clone    = bool(combined >= THRESHOLDS['type3']['clone'])
        confidence  = self._get_type3_confidence(combined)
        details     = hybrid.get("details", {})

        return Type3Result(
            score=round(combined, 4),
            is_clone=is_clone,
            confidence=confidence,
            details={
                "hybrid_score":        round(hybrid_score, 4),
                "ml_score":            round(ml_score, 4) if ml_score is not None else None,
                "structural_fragment": round(details.get("structural_fragment_score", 0.0), 4),
                "winnowing":           round(details.get("winnowing_fingerprint_score", 0.0), 4),
                "ast":                 round(details.get("ast_skeleton_score", 0.0), 4),
                "metrics":             round(details.get("complexity_metric_score", 0.0), 4),
                "discrimination":      raw.get("clone_type_discrimination", {}),
            }
        )

    def _process_type4_result(self, raw: Dict) -> Type4Result:
        """Process raw Type-4 detector output"""
        score      = raw["semantic_score"]
        confidence = self._get_type4_confidence(score)
        return Type4Result(
            score=round(score, 4),
            is_clone=raw["is_semantic_clone"],
            confidence=confidence,
            category_scores=raw.get("category_scores", {}),
        )

    def _get_type3_confidence(self, score: float) -> str:
        if score >= THRESHOLDS['type3']['critical']: return 'CRITICAL'
        if score >= THRESHOLDS['type3']['high']:     return 'HIGH'
        if score >= THRESHOLDS['type3']['clone']:    return 'MEDIUM'
        if score >= 0.40:                            return 'LOW'
        return 'UNLIKELY'

    def _get_type4_confidence(self, score: float) -> str:
        if score >= THRESHOLDS['type4']['critical']: return 'CRITICAL'
        if score >= THRESHOLDS['type4']['high']:     return 'HIGH'
        if score >= THRESHOLDS['type4']['clone']:    return 'MEDIUM'
        if score >= 0.40:                            return 'LOW'
        return 'UNLIKELY'

    # =========================================================================
    # CLONE TYPE DETERMINATION
    # =========================================================================

    def _determine_primary_clone_type(
        self,
        type1_score:         float,
        type2_score:         float,
        type3_score:         float,
        type4_score:         float,
        cross_layer_result = None,
    ) -> str:
        """
        Priority order: Type-1 > Type-2 > Type-3 > Type-4 > cross_layer > none.
        Cross-layer only wins when all the traditional scores are below threshold,
        because it's a different kind of finding — not plagiarism per se, but
        shared feature implementation across architectural layers.
        """
        if type1_score >= 0.95:  return "type1"
        if type2_score >= 0.65:  return "type2"
        if type3_score >= 0.50:  return "type3"
        if type4_score >= 0.70:  return "type4"
        # Only declare cross_layer if there are actual matches
        if (cross_layer_result
                and cross_layer_result.is_cross_layer
                and cross_layer_result.matches):
            return "cross_layer"
        return "none"

    def _determine_clone_type(
        self,
        type3:         Type3Result,
        type4:         Type4Result,
        cross_layer = None,
    ) -> CloneType:
        type3_high = type3.confidence in ('HIGH', 'CRITICAL')
        type4_high = type4.confidence in ('HIGH', 'CRITICAL')

        if type3_high and type4_high:              return CloneType.TYPE3_AND_TYPE4
        if type3_high:                             return CloneType.TYPE3
        if type4_high:                             return CloneType.TYPE4
        if type3.is_clone and type4.is_clone:      return CloneType.TYPE3_AND_TYPE4
        if type3.is_clone:                         return CloneType.TYPE3
        if type4.is_clone:                         return CloneType.TYPE4
        # Fall through to cross-layer if nothing else fired
        if cross_layer and cross_layer.is_cross_layer and cross_layer.matches:
            return CloneType.CROSS_LAYER
        return CloneType.NONE

    def _determine_risk_level(
        self,
        type3:         Type3Result,
        type4:         Type4Result,
        cross_layer = None,
    ) -> RiskLevel:
        if type3.confidence == 'CRITICAL' or type4.confidence == 'CRITICAL': return RiskLevel.CRITICAL
        if type3.confidence == 'HIGH'     or type4.confidence == 'HIGH':     return RiskLevel.HIGH
        if type3.is_clone or type4.is_clone:                                 return RiskLevel.MEDIUM
        if type3.confidence == 'LOW'      or type4.confidence == 'LOW':      return RiskLevel.LOW
        # Cross-layer matches are LOW risk by default — interesting, not alarming
        if cross_layer and cross_layer.is_cross_layer and cross_layer.matches:
            return RiskLevel.LOW
        return RiskLevel.NONE

    def _determine_review_action(self, risk_level: RiskLevel) -> ReviewAction:
        mapping = {
            RiskLevel.CRITICAL: ReviewAction.IMMEDIATE_REVIEW,
            RiskLevel.HIGH:     ReviewAction.SCHEDULED_REVIEW,
            RiskLevel.MEDIUM:   ReviewAction.MANUAL_CHECK,
            RiskLevel.LOW:      ReviewAction.NOTE_ONLY,
            RiskLevel.NONE:     ReviewAction.NO_ACTION,
        }
        return mapping.get(risk_level, ReviewAction.NO_ACTION)

    def _generate_explanation(
        self,
        type3:         Type3Result,
        type4:         Type4Result,
        clone_type:    CloneType,
        primary_clone_type: str = "none",
        cross_layer = None,
    ) -> str:
        type_labels = {
            "type1":       "Type-1 (Exact Copy)",
            "type2":       "Type-2 (Renamed Variables)",
            "type3":       "Type-3 (Structural Clone)",
            "type4":       "Type-4 (Semantic Clone)",
            "cross_layer": "Cross-Layer Feature Match",
            "none":        "No significant clone",
        }
        primary_label = type_labels.get(primary_clone_type, "Unknown")

        if clone_type == CloneType.TYPE3_AND_TYPE4:
            return (
                f"⚠️ STRONG EVIDENCE [{primary_label}]: Code is structurally similar "
                f"(Type-3: {type3.confidence}, score: {type3.score}) AND behaves the same "
                f"(Type-4: {type4.confidence}, score: {type4.score})."
            )
        if clone_type == CloneType.TYPE3:
            return (
                f"📋 STRUCTURAL CLONE [{primary_label}]: Code structure is similar "
                f"(Type-3: {type3.confidence}, score: {type3.score})."
            )
        if clone_type == CloneType.TYPE4:
            return (
                f"🧠 SEMANTIC CLONE [{primary_label}]: Code behaves similarly "
                f"(Type-4: {type4.confidence}, score: {type4.score})."
            )
        if clone_type == CloneType.CROSS_LAYER and cross_layer:
            n_matches = len(cross_layer.matches)
            return (
                f"🌐 CROSS-LAYER MATCH [{primary_label}]: "
                f"{n_matches} shared function(s) found across "
                f"{cross_layer.layer_a.value} ↔ {cross_layer.layer_b.value} "
                f"(score: {cross_layer.cross_layer_score:.2f}). {cross_layer.explanation}"
            )
        return f"✅ No significant clone detected. Primary: {primary_label}"

    # =========================================================================
    # BATCH STATISTICS
    # =========================================================================

    def _calculate_batch_stats(self, results: List[UnifiedResult]) -> Dict:
        if not results:
            return {"total_pairs": 0}

        cross_layer_pairs = sum(
            1 for r in results
            if r.cross_layer and r.cross_layer.is_cross_layer and r.cross_layer.matches
        )

        return {
            "total_pairs":      len(results),
            "clones_detected":  sum(1 for r in results if r.clone_type != "NONE"),
            "needs_review":     sum(1 for r in results if r.needs_teacher_review),
            "risk_breakdown": {
                "critical": sum(1 for r in results if r.risk_level == "CRITICAL"),
                "high":     sum(1 for r in results if r.risk_level == "HIGH"),
                "medium":   sum(1 for r in results if r.risk_level == "MEDIUM"),
                "low":      sum(1 for r in results if r.risk_level == "LOW"),
            },
            "clone_type_breakdown": {
                "type1":       sum(1 for r in results if r.primary_clone_type == "type1"),
                "type2":       sum(1 for r in results if r.primary_clone_type == "type2"),
                "type3":       sum(1 for r in results if r.primary_clone_type == "type3"),
                "type4":       sum(1 for r in results if r.primary_clone_type == "type4"),
                "cross_layer": sum(1 for r in results if r.primary_clone_type == "cross_layer"),
                "none":        sum(1 for r in results if r.primary_clone_type == "none"),
            },
            "cross_layer_pairs":    cross_layer_pairs,
            "average_combined_score": round(
                sum(r.combined_score for r in results) / len(results), 4
            ),
        }

    def _generate_teacher_summary(
        self,
        results: List[UnifiedResult],
        stats:   Dict,
    ) -> str:
        n           = stats.get("total_pairs", 0)
        critical    = stats.get("risk_breakdown", {}).get("critical", 0)
        high        = stats.get("risk_breakdown", {}).get("high", 0)
        cross_layer = stats.get("cross_layer_pairs", 0)

        if critical > 0:
            return f"🚨 {critical} CRITICAL pair(s) found out of {n}. Immediate review recommended."
        if high > 0:
            return f"⚠️ {high} HIGH-risk pair(s) found out of {n}. Scheduled review recommended."
        if cross_layer > 0:
            return (
                f"🌐 {cross_layer} cross-layer feature match(es) found across {n} comparison(s). "
                f"This suggests shared feature implementation across architectural layers."
            )
        return f"✅ No high-risk pairs found among {n} comparisons."
