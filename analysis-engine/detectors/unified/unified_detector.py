# analysis-engine/detectors/unified/unified_detector.py

"""
Unified Clone Detection Engine

Combines Type-3 (structural) and Type-4 (semantic) detection to provide:
- SEPARATE results for Type-3 and Type-4
- COMBINED verdict with risk level
- Teacher-friendly summary with action items

Key Features:
- Shows both detector results independently
- Determines clone type (TYPE3, TYPE4, TYPE3_AND_TYPE4, NONE)
- Calculates risk level (CRITICAL, HIGH, MEDIUM, LOW, NONE)
- Flags pairs needing teacher review (>= 70% combined)
- Provides human-readable explanations
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
    TYPE3 = "TYPE3"                     # Structural clone (copy-paste)
    TYPE4 = "TYPE4"                     # Semantic clone (different code, same behavior)
    TYPE3_AND_TYPE4 = "TYPE3_AND_TYPE4" # Both detected (strongest evidence)
    NONE = "NONE"                       # Not a clone


class RiskLevel(Enum):
    """Risk level for plagiarism"""
    CRITICAL = "CRITICAL"       # Immediate action needed
    HIGH = "HIGH"               # Strong evidence
    MEDIUM = "MEDIUM"           # Needs review
    LOW = "LOW"                 # Minor concern
    NONE = "NONE"               # No concern


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
        'clone': 0.50,       # Score >= this = clone detected
        'high': 0.70,        # Score >= this = HIGH confidence
        'critical': 0.85,    # Score >= this = CRITICAL
    },
    'type4': {
        'clone': 0.60,
        'high': 0.80,
        'critical': 0.90,
    },
    'teacher_review': 0.70,  # Combined score >= this = needs teacher review
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
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON response"""
        return {
            "file_a": self.file_a,
            "file_b": self.file_b,
            
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
            }
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

        # type1/type2 scores feed into combined score
        type1_score = type1_raw.get("type1_score", 0.0)
        type2_score = type2_raw.get("type2_score", 0.0)

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
        explanation    = self._generate_explanation(type3_result, type4_result, clone_type)

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
        )
        # attach type1/2 for callers that want them
        result.type1_score = round(type1_score, 4)
        result.type2_score = round(type2_score, 4)
        return result

    def detect_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Run unified detection on multiple files.
        Only compares files of the SAME LANGUAGE (all 4 detector types).
        """
        from engine.analyzer import build_same_language_pairs

        start_time = time.time()
        results: List[UnifiedResult] = []
        n = len(file_paths)

        # Same-language pairs only — mirrors NiCad / PMD behaviour
        same_lang_pairs = build_same_language_pairs(file_paths)
        total_comparisons = len(same_lang_pairs)

        print(f"🔍 Comparing {n} files → {total_comparisons} same-language pairs...")

        # Prepare Type-3 batch (frequency filter across ALL files is fine)
        self.type3_detector.prepare_batch([Path(p) for p in file_paths])

        # Clear Type-4 cache for fresh batch
        self.type4_detector.clear_cache()

        # Compare same-language pairs only (Types 1-4 all applied)
        for file_a, file_b in same_lang_pairs:
            result = self.detect(file_a, file_b)
            results.append(result)
        
        # Sort by risk (CRITICAL first) then by combined score
        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'NONE': 4}
        results.sort(key=lambda x: (risk_order.get(x.risk_level, 5), -x.combined_score))
        
        # Calculate statistics
        stats = self._calculate_batch_stats(results)
        
        # Generate teacher summary
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
        """Process raw Type-3 detector output — FIXED for new hybrid_detector"""
        hybrid = raw["hybrid"]
        ml = raw.get("ml")
        
        hybrid_score = hybrid["score"]
        ml_score = ml["score"] if ml else 0.0
        combined = (hybrid_score * 0.5) + (ml_score * 0.5)
        
        # Use combined score for verdict (not AND logic — old approach was too strict)
        is_clone = bool(combined >= THRESHOLDS['type3']['clone'])
        
        # Determine confidence
        confidence = self._get_type3_confidence(combined)
        
        # Read detail keys that match new hybrid_detector output
        details = hybrid.get("details", {})
        
        return Type3Result(
            score=round(combined, 4),
            is_clone=is_clone,
            confidence=confidence,
            details={
                "hybrid_score": round(hybrid_score, 4),
                "ml_score": round(ml_score, 4) if ml else None,
                "structural_fragment": round(details.get("structural_fragment_score", 0.0), 4),
                "winnowing": round(details.get("winnowing_fingerprint_score", 0.0), 4),
                "ast": round(details.get("ast_skeleton_score", 0.0), 4),
                "metrics": round(details.get("complexity_metric_score", 0.0), 4),
                # NEW: discrimination info for debugging/logging
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
        """Get Type-3 confidence level"""
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
        """Get Type-4 confidence level"""
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
    # VERDICT DETERMINATION
    # =========================================================================
    
    def _determine_clone_type(
        self, 
        type3: Type3Result, 
        type4: Type4Result
    ) -> CloneType:
        """
        Determine the PRIMARY clone type.
        
        Logic:
        - Both HIGH/CRITICAL → TYPE3_AND_TYPE4 (strongest evidence)
        - Type3 HIGH only → TYPE3 (structural clone)
        - Type4 HIGH only → TYPE4 (semantic clone)
        - Neither HIGH → based on which detected clone
        """
        type3_high = type3.confidence in ['HIGH', 'CRITICAL']
        type4_high = type4.confidence in ['HIGH', 'CRITICAL']
        
        if type3_high and type4_high:
            return CloneType.TYPE3_AND_TYPE4
        elif type3_high:
            return CloneType.TYPE3
        elif type4_high:
            return CloneType.TYPE4
        elif type3.is_clone and type4.is_clone:
            # Both detected but not HIGH
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
        """Determine risk level based on both scores."""
        
        # If either is CRITICAL
        if type3.confidence == 'CRITICAL' or type4.confidence == 'CRITICAL':
            return RiskLevel.CRITICAL
        
        # If both are HIGH
        if type3.confidence == 'HIGH' and type4.confidence == 'HIGH':
            return RiskLevel.CRITICAL
        
        # If one is HIGH
        if type3.confidence == 'HIGH' or type4.confidence == 'HIGH':
            return RiskLevel.HIGH
        
        # If both are MEDIUM
        if type3.confidence == 'MEDIUM' and type4.confidence == 'MEDIUM':
            return RiskLevel.MEDIUM
        
        # If one is MEDIUM
        if type3.confidence == 'MEDIUM' or type4.confidence == 'MEDIUM':
            return RiskLevel.LOW
        
        return RiskLevel.NONE
    
    def _determine_review_action(self, risk: RiskLevel) -> ReviewAction:
        """Determine what action teacher should take."""
        
        action_map = {
            RiskLevel.CRITICAL: ReviewAction.IMMEDIATE_REVIEW,
            RiskLevel.HIGH: ReviewAction.SCHEDULED_REVIEW,
            RiskLevel.MEDIUM: ReviewAction.MANUAL_CHECK,
            RiskLevel.LOW: ReviewAction.NOTE_ONLY,
            RiskLevel.NONE: ReviewAction.NO_ACTION,
        }
        return action_map.get(risk, ReviewAction.NO_ACTION)
    
    def _generate_explanation(
        self,
        type3: Type3Result,
        type4: Type4Result,
        clone_type: CloneType
    ) -> str:
        """Generate human-readable explanation."""
        
        if clone_type == CloneType.TYPE3_AND_TYPE4:
            return (
                f"⚠️ STRONG EVIDENCE: Code is structurally similar (Type-3: {type3.confidence}, "
                f"score: {type3.score}) AND behaves the same (Type-4: {type4.confidence}, "
                f"score: {type4.score}). This strongly suggests copy-paste plagiarism."
            )
        
        elif clone_type == CloneType.TYPE3:
            return (
                f"📋 STRUCTURAL CLONE: Code structure is similar (Type-3: {type3.confidence}, "
                f"score: {type3.score}) but semantic behavior differs (Type-4: {type4.confidence}, "
                f"score: {type4.score}). Could be copied template or partial plagiarism."
            )
        
        elif clone_type == CloneType.TYPE4:
            return (
                f"🧠 SEMANTIC CLONE: Code looks different (Type-3: {type3.confidence}, "
                f"score: {type3.score}) but behaves the same (Type-4: {type4.confidence}, "
                f"score: {type4.score}). Could be same algorithm independently written, "
                f"or sophisticated plagiarism with code rewriting."
            )
        
        else:
            return (
                f"✅ NO SIGNIFICANT CLONE: Type-3: {type3.confidence} (score: {type3.score}), "
                f"Type-4: {type4.confidence} (score: {type4.score}). "
                f"No evidence of cloning detected."
            )
    
    # =========================================================================
    # BATCH STATISTICS
    # =========================================================================
    
    def _calculate_batch_stats(self, results: List[UnifiedResult]) -> Dict:
        """Calculate batch statistics."""
        
        # Clone type counts
        clone_counts = {ct.value: 0 for ct in CloneType}
        for r in results:
            clone_counts[r.clone_type] += 1
        
        # Risk level counts
        risk_counts = {rl.value: 0 for rl in RiskLevel}
        for r in results:
            risk_counts[r.risk_level] += 1
        
        # Teacher review count
        needs_review = sum(1 for r in results if r.needs_teacher_review)
        
        # Type-3 specific
        type3_clones = sum(1 for r in results if r.type3.is_clone)
        type3_high = sum(1 for r in results if r.type3.confidence in ['HIGH', 'CRITICAL'])
        
        # Type-4 specific
        type4_clones = sum(1 for r in results if r.type4.is_clone)
        type4_high = sum(1 for r in results if r.type4.confidence in ['HIGH', 'CRITICAL'])
        
        return {
            "clone_type_breakdown": clone_counts,
            "risk_level_breakdown": risk_counts,
            "needs_teacher_review_count": needs_review,
            
            "type3_summary": {
                "total_clones": type3_clones,
                "high_confidence": type3_high,
            },
            
            "type4_summary": {
                "total_clones": type4_clones,
                "high_confidence": type4_high,
            },
        }
    
    def _generate_teacher_summary(
        self, 
        results: List[UnifiedResult], 
        stats: Dict
    ) -> Dict:
        """Generate summary specifically for teacher review."""
        
        # Get critical and high risk pairs
        critical_pairs = [
            {
                "file_a": r.file_a, 
                "file_b": r.file_b, 
                "combined_score": r.combined_score,
                "clone_type": r.clone_type,
            }
            for r in results if r.risk_level == "CRITICAL"
        ]
        
        high_risk_pairs = [
            {
                "file_a": r.file_a, 
                "file_b": r.file_b, 
                "combined_score": r.combined_score,
                "clone_type": r.clone_type,
            }
            for r in results if r.risk_level == "HIGH"
        ]
        
        # Determine overall concern level
        critical_count = stats["risk_level_breakdown"]["CRITICAL"]
        high_count = stats["risk_level_breakdown"]["HIGH"]
        total = len(results)
        
        if critical_count > 0:
            concern_level = "CRITICAL"
            message = f"🚨 ALERT: {critical_count} pair(s) require IMMEDIATE review!"
        elif high_count > total * 0.2:
            concern_level = "HIGH"
            message = f"⚠️ WARNING: {high_count} pair(s) show high similarity. Class-wide review recommended."
        elif high_count > 0:
            concern_level = "MEDIUM"
            message = f"📋 NOTICE: {high_count} pair(s) need attention."
        else:
            concern_level = "LOW"
            message = "✅ No significant plagiarism concerns detected."
        
        return {
            "concern_level": concern_level,
            "message": message,
            "action_required": critical_count > 0 or high_count > 0,
            "critical_pairs": critical_pairs[:10],  # Top 10
            "high_risk_pairs": high_risk_pairs[:10],  # Top 10
            "total_needing_review": stats["needs_teacher_review_count"],
        }