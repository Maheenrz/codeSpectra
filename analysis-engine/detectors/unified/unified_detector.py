# analysis-engine/detectors/unified/unified_detector.py

"""
Unified Clone Detection Engine — FIXED v2.1

Fixes:
  1. _process_type3_result uses OR logic for combined score (not AND)
  2. If ML unavailable, uses hybrid score alone
  3. _determine_clone_type now uses type1/type2 scores too
  4. to_dict includes type1_score and type2_score
"""

from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import time
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# NEW:
from detectors.type1.type1_detector import Type1Detector
from detectors.type2.type2_detector import Type2Detector
from detectors.type3.hybrid_detector import Type3HybridDetector
from detectors.type4.type4_detector import Type4Detector

# =============================================================================
# ENUMS
# =============================================================================

class CloneType(Enum):
    """Primary clone type detected"""
    TYPE1 = "TYPE1"
    TYPE2 = "TYPE2"
    TYPE3 = "TYPE3"
    TYPE4 = "TYPE4"
    TYPE3_AND_TYPE4 = "TYPE3_AND_TYPE4"
    NONE = "NONE"


class RiskLevel(Enum):
    """Risk level for plagiarism"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class ReviewAction(Enum):
    """Recommended action for teacher"""
    IMMEDIATE_REVIEW = "IMMEDIATE_REVIEW"
    SCHEDULED_REVIEW = "SCHEDULED_REVIEW"
    MANUAL_CHECK = "MANUAL_CHECK"
    NOTE_ONLY = "NOTE_ONLY"
    NO_ACTION = "NO_ACTION"


# =============================================================================
# CONFIGURATION
# =============================================================================

THRESHOLDS = {
    'type3': {
        'clone': 0.50,
        'high': 0.70,
        'critical': 0.85,
    },
    'type4': {
        'clone': 0.60,
        'high': 0.80,
        'critical': 0.90,
    },
    'teacher_review': 0.70,
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Type3Result:
    """Type-3 detection result (shown separately)"""
    score: float
    is_clone: bool
    confidence: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Type4Result:
    """Type-4 detection result (shown separately)"""
    score: float
    is_clone: bool
    confidence: str
    category_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class UnifiedResult:
    """Complete unified detection result"""
    file_a: str
    file_b: str
    
    # SEPARATE results
    type3: Type3Result
    type4: Type4Result
    
    # COMBINED verdict
    clone_type: str
    risk_level: str
    combined_score: float
    
    # Teacher guidance
    needs_teacher_review: bool
    review_action: str
    explanation: str
    
    # NEW: individual type scores
    type1_score: float = 0.0
    type2_score: float = 0.0
    primary_clone_type: str = "none"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON response"""
        return {
            "file_a": self.file_a,
            "file_b": self.file_b,
            
            # ── NEW: type1 and type2 scores ──────────────────────────
            "type1_score": self.type1_score,
            "type2_score": self.type2_score,
            "primary_clone_type": self.primary_clone_type,
            
            # Type-3 Results (SEPARATE)
            "type3": {
                "score": self.type3.score,
                "is_clone": self.type3.is_clone,
                "confidence": self.type3.confidence,
                "details": self.type3.details,
            },
            
            # Type-4 Results (SEPARATE)
            "type4": {
                "score": self.type4.score,
                "is_clone": self.type4.is_clone,
                "confidence": self.type4.confidence,
                "category_scores": self.type4.category_scores,
            },
            
            # Combined Verdict
            "verdict": {
                "clone_type": self.clone_type,
                "risk_level": self.risk_level,
                "combined_score": self.combined_score,
                "needs_teacher_review": self.needs_teacher_review,
                "review_action": self.review_action,
                "explanation": self.explanation,
            },
            
            # Structural/semantic aliases for frontend compatibility
            "structural": {
                "score": self.type3.score,
                "confidence": self.type3.confidence,
                "is_similar": self.type3.is_clone,
            },
            "semantic": {
                "score": self.type4.score,
                "confidence": self.type4.confidence,
                "is_similar": self.type4.is_clone,
            },
        }


# =============================================================================
# UNIFIED DETECTOR
# =============================================================================

class UnifiedDetector:
    """
    Unified Clone Detection Engine
    
    Usage:
        detector = UnifiedDetector()
        
        # Single pair
        result = detector.detect("file1.cpp", "file2.cpp")
        
        # Batch (multiple files)
        results = detector.detect_batch(["file1.cpp", "file2.cpp", "file3.cpp"])
    """
    
    def __init__(
        self,
        type3_hybrid_threshold: float = 0.50,
        type3_ml_threshold: float = 0.60,
        type4_threshold: float = 0.60,
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
        print("✅ Unified Detector Initialized (Type 1–4)")

    # =========================================================================
    # MAIN DETECTION METHODS
    # =========================================================================
    
    def detect(self, file_path_a: str, file_path_b: str) -> UnifiedResult:
        file_a = Path(file_path_a)
        file_b = Path(file_path_b)

        # Run all 4 detectors
        type1_raw = self.type1_detector.detect(str(file_a), str(file_b))
        type2_raw = self.type2_detector.detect(str(file_a), str(file_b))
        type3_raw = self.type3_detector.detect(file_a, file_b)
        type4_raw = self.type4_detector.detect(str(file_a), str(file_b))

        type3_result = self._process_type3_result(type3_raw)
        type4_result = self._process_type4_result(type4_raw)

        type1_score = type1_raw.get("type1_score", 0.0)
        type2_score = type2_raw.get("type2_score", 0.0)

        # ── Determine primary clone type using all 4 scores ──────────────
        primary_clone_type = self._determine_primary_clone_type(
            type1_score, type2_score, type3_result.score, type4_result.score
        )
        
        clone_type    = self._determine_clone_type(type3_result, type4_result)
        risk_level    = self._determine_risk_level(type3_result, type4_result)
        combined_score = (
            type1_score  * 0.10 +
            type2_score  * 0.15 +
            type3_result.score * 0.45 +
            type4_result.score * 0.30
        )

        needs_review   = combined_score >= self.teacher_review_threshold
        review_action  = self._determine_review_action(risk_level)
        explanation    = self._generate_explanation(
            type3_result, type4_result, clone_type, primary_clone_type
        )

        result = UnifiedResult(
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
        )
        return result

    def detect_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        from engine.analyzer import build_same_language_pairs

        start_time = time.time()
        results: List[UnifiedResult] = []
        n = len(file_paths)

        same_lang_pairs = build_same_language_pairs(file_paths)
        total_comparisons = len(same_lang_pairs)

        print(f"🔍 Comparing {n} files → {total_comparisons} same-language pairs...")

        self.type3_detector.prepare_batch([Path(p) for p in file_paths])
        self.type4_detector.clear_cache()

        for file_a, file_b in same_lang_pairs:
            result = self.detect(file_a, file_b)
            results.append(result)
        
        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'NONE': 4}
        results.sort(key=lambda x: (risk_order.get(x.risk_level, 5), -x.combined_score))
        
        stats = self._calculate_batch_stats(results)
        teacher_summary = self._generate_teacher_summary(results, stats)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "total_files": n,
            "total_comparisons": total_comparisons,
            "processing_time_ms": round(processing_time, 2),
            "statistics": stats,
            "teacher_summary": teacher_summary,
            "results": [r.to_dict() for r in results],
        }
    
    # =========================================================================
    # RESULT PROCESSING
    # =========================================================================
    
    def _process_type3_result(self, raw: Dict) -> Type3Result:
        """Process raw Type-3 detector output — FIXED"""
        hybrid = raw["hybrid"]
        ml = raw.get("ml")
        
        hybrid_score = hybrid["score"]
        ml_score = ml["score"] if ml else None
        
        # ── FIX: Don't average with 0 when ML unavailable ────────────────
        if ml_score is not None:
            combined = (hybrid_score * 0.6) + (ml_score * 0.4)
        else:
            combined = hybrid_score
        
        is_clone = bool(combined >= THRESHOLDS['type3']['clone'])
        confidence = self._get_type3_confidence(combined)
        
        details = hybrid.get("details", {})
        
        return Type3Result(
            score=round(combined, 4),
            is_clone=is_clone,
            confidence=confidence,
            details={
                "hybrid_score": round(hybrid_score, 4),
                "ml_score": round(ml_score, 4) if ml_score is not None else None,
                "structural_fragment": round(details.get("structural_fragment_score", 0.0), 4),
                "winnowing": round(details.get("winnowing_fingerprint_score", 0.0), 4),
                "ast": round(details.get("ast_skeleton_score", 0.0), 4),
                "metrics": round(details.get("complexity_metric_score", 0.0), 4),
                "discrimination": raw.get("clone_type_discrimination", {}),
            }
        )

    def _process_type4_result(self, raw: Dict) -> Type4Result:
        """Process raw Type-4 detector output"""
        score = raw["semantic_score"]
        confidence = self._get_type4_confidence(score)
        
        return Type4Result(
            score=round(score, 4),
            is_clone=raw["is_semantic_clone"],
            confidence=confidence,
            category_scores=raw.get("category_scores", {}),
        )
    
    def _get_type3_confidence(self, score: float) -> str:
        if score >= THRESHOLDS['type3']['critical']:
            return 'CRITICAL'
        elif score >= THRESHOLDS['type3']['high']:
            return 'HIGH'
        elif score >= THRESHOLDS['type3']['clone']:
            return 'MEDIUM'
        elif score >= 0.40:
            return 'LOW'
        else:
            return 'UNLIKELY'
    
    def _get_type4_confidence(self, score: float) -> str:
        if score >= THRESHOLDS['type4']['critical']:
            return 'CRITICAL'
        elif score >= THRESHOLDS['type4']['high']:
            return 'HIGH'
        elif score >= THRESHOLDS['type4']['clone']:
            return 'MEDIUM'
        elif score >= 0.40:
            return 'LOW'
        else:
            return 'UNLIKELY'
    
    # =========================================================================
    # CLONE TYPE DETERMINATION
    # =========================================================================
    
    def _determine_primary_clone_type(
        self,
        type1_score: float,
        type2_score: float,
        type3_score: float,
        type4_score: float,
    ) -> str:
        """
        Same logic as analyzer.py — uses all 4 scores.
        Priority: Type-1 > Type-2 > Type-3 > Type-4 > none
        """
        if type1_score >= 0.95:
            return "type1"
        if type2_score >= 0.80:
            return "type2"
        if type3_score >= 0.50:
            return "type3"
        if type4_score >= 0.60:
            return "type4"
        return "none"

    def _determine_clone_type(
        self, 
        type3: Type3Result, 
        type4: Type4Result
    ) -> CloneType:
        type3_high = type3.confidence in ['HIGH', 'CRITICAL']
        type4_high = type4.confidence in ['HIGH', 'CRITICAL']
        
        if type3_high and type4_high:
            return CloneType.TYPE3_AND_TYPE4
        elif type3_high:
            return CloneType.TYPE3
        elif type4_high:
            return CloneType.TYPE4
        elif type3.is_clone and type4.is_clone:
            return CloneType.TYPE3_AND_TYPE4
        elif type3.is_clone:
            return CloneType.TYPE3
        elif type4.is_clone:
            return CloneType.TYPE4
        else:
            return CloneType.NONE
    
    def _determine_risk_level(
        self, 
        type3: Type3Result, 
        type4: Type4Result
    ) -> RiskLevel:
        if type3.confidence == 'CRITICAL' or type4.confidence == 'CRITICAL':
            return RiskLevel.CRITICAL
        elif type3.confidence == 'HIGH' or type4.confidence == 'HIGH':
            return RiskLevel.HIGH
        elif type3.is_clone or type4.is_clone:
            return RiskLevel.MEDIUM
        elif type3.confidence == 'LOW' or type4.confidence == 'LOW':
            return RiskLevel.LOW
        else:
            return RiskLevel.NONE
    
    def _determine_review_action(self, risk_level: RiskLevel) -> ReviewAction:
        if risk_level == RiskLevel.CRITICAL:
            return ReviewAction.IMMEDIATE_REVIEW
        elif risk_level == RiskLevel.HIGH:
            return ReviewAction.SCHEDULED_REVIEW
        elif risk_level == RiskLevel.MEDIUM:
            return ReviewAction.MANUAL_CHECK
        elif risk_level == RiskLevel.LOW:
            return ReviewAction.NOTE_ONLY
        else:
            return ReviewAction.NO_ACTION
    
    def _generate_explanation(
        self,
        type3: Type3Result,
        type4: Type4Result,
        clone_type: CloneType,
        primary_clone_type: str = "none"
    ) -> str:
        type_labels = {
            "type1": "Type-1 (Exact Copy)",
            "type2": "Type-2 (Renamed Variables)",
            "type3": "Type-3 (Structural Clone)",
            "type4": "Type-4 (Semantic Clone)",
            "none":  "No significant clone",
        }
        primary_label = type_labels.get(primary_clone_type, "Unknown")
        
        if clone_type == CloneType.TYPE3_AND_TYPE4:
            return (
                f"⚠️ STRONG EVIDENCE [{primary_label}]: Code is structurally similar "
                f"(Type-3: {type3.confidence}, score: {type3.score}) AND behaves the same "
                f"(Type-4: {type4.confidence}, score: {type4.score})."
            )
        elif clone_type == CloneType.TYPE3:
            return (
                f"📋 STRUCTURAL CLONE [{primary_label}]: Code structure is similar "
                f"(Type-3: {type3.confidence}, score: {type3.score})."
            )
        elif clone_type == CloneType.TYPE4:
            return (
                f"🧠 SEMANTIC CLONE [{primary_label}]: Code behaves similarly "
                f"(Type-4: {type4.confidence}, score: {type4.score})."
            )
        else:
            return f"✅ No significant clone detected. Primary: {primary_label}"
    
    # =========================================================================
    # BATCH STATISTICS
    # =========================================================================
    
    def _calculate_batch_stats(self, results: List[UnifiedResult]) -> Dict:
        if not results:
            return {"total_pairs": 0}
        
        return {
            "total_pairs": len(results),
            "clones_detected": sum(1 for r in results if r.clone_type != "NONE"),
            "needs_review": sum(1 for r in results if r.needs_teacher_review),
            "risk_breakdown": {
                "critical": sum(1 for r in results if r.risk_level == "CRITICAL"),
                "high": sum(1 for r in results if r.risk_level == "HIGH"),
                "medium": sum(1 for r in results if r.risk_level == "MEDIUM"),
                "low": sum(1 for r in results if r.risk_level == "LOW"),
            },
            "clone_type_breakdown": {
                "type1": sum(1 for r in results if r.primary_clone_type == "type1"),
                "type2": sum(1 for r in results if r.primary_clone_type == "type2"),
                "type3": sum(1 for r in results if r.primary_clone_type == "type3"),
                "type4": sum(1 for r in results if r.primary_clone_type == "type4"),
                "none":  sum(1 for r in results if r.primary_clone_type == "none"),
            },
            "average_combined_score": round(
                sum(r.combined_score for r in results) / len(results), 4
            ),
        }
    
    def _generate_teacher_summary(
        self, 
        results: List[UnifiedResult], 
        stats: Dict
    ) -> str:
        n = stats.get("total_pairs", 0)
        critical = stats.get("risk_breakdown", {}).get("critical", 0)
        high = stats.get("risk_breakdown", {}).get("high", 0)
        
        if critical > 0:
            return (
                f"🚨 {critical} CRITICAL pair(s) found out of {n}. "
                f"Immediate review recommended."
            )
        elif high > 0:
            return (
                f"⚠️ {high} HIGH-risk pair(s) found out of {n}. "
                f"Scheduled review recommended."
            )
        else:
            return f"✅ No high-risk pairs found among {n} comparisons."