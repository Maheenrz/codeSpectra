# analysis-engine/engine/analyzer.py

"""
CodeSpectra Clone Analyzer
==========================

A code clone detection engine for educational institutions.

Detects two types of similarity:
1. Structural Similarity - Code that looks similar (copy-paste, renaming)
2. Semantic Similarity - Code that behaves similarly (different code, same logic)

Output Modes:
- Summary: High-level scores for quick review
- Detailed: Full breakdown (winnowing, AST, data-flow, control-flow, etc.)

Based on research methodologies from MOSS, JPlag, and BigCloneBench.

Author: CodeSpectra Team
Version: 2.0.0
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import time
import sys

# Ensure imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class AnalyzerConfig:
    """Analyzer configuration"""
    
    # Structural detection thresholds
    structural_threshold: float = 0.50
    structural_high: float = 0.70
    ml_threshold: float = 0.60
    
    # Semantic detection thresholds
    semantic_threshold: float = 0.60
    semantic_high: float = 0.80
    
    # Class-wide analysis
    class_high_similarity_threshold: float = 0.70
    simple_problem_ratio: float = 0.70
    
    # Review flags
    review_threshold: float = 0.70

    type1_threshold: float = 0.98
    type2_threshold: float = 0.90

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class StructuralDetails:
    """Detailed structural analysis breakdown"""
    winnowing_score: float
    ast_score: float
    metrics_score: float
    ml_score: Optional[float]
    hybrid_score: float


@dataclass
class SemanticDetails:
    """Detailed semantic analysis breakdown"""
    control_flow_score: float
    data_flow_score: float
    call_pattern_score: float
    structural_score: float
    behavioral_score: float
    behavioral_hash_a: str
    behavioral_hash_b: str


@dataclass
class StructuralResult:
    """Structural analysis result"""
    score: float
    is_similar: bool
    confidence: str
    details: Optional[StructuralDetails] = None


@dataclass
class SemanticResult:
    """Semantic analysis result"""
    score: float
    is_similar: bool
    confidence: str
    details: Optional[SemanticDetails] = None


@dataclass
class PairResult:
    """Analysis result for a file pair"""
    file_a: str
    file_b: str
    structural: StructuralResult
    semantic: SemanticResult
    similarity_level: str  # HIGH, MEDIUM, LOW, NONE
    needs_review: bool
    summary: str
    type1_score: float = 0.0
    type2_score: float = 0.0


@dataclass
class ClassAnalysis:
    """Class-wide pattern analysis"""
    is_simple_problem: bool
    high_similarity_ratio: float
    average_structural: float
    average_semantic: float
    message: str
    outlier_pairs: List[Dict] = field(default_factory=list)


# =============================================================================
# CLONE ANALYZER
# =============================================================================

class CloneAnalyzer:
    """
    CodeSpectra Clone Analyzer
    
    Usage:
        analyzer = CloneAnalyzer()
        
        # Get summary results (for list view)
        report = analyzer.analyze(file_paths, detailed=False)
        
        # Get detailed results (for detailed view)
        report = analyzer.analyze(file_paths, detailed=True)
        
        # Get details for specific pair
        pair_detail = analyzer.get_pair_details(file_a, file_b)
    """
    
    def __init__(self, config: AnalyzerConfig = None):
        """Initialize analyzer with configuration"""
        self.config = config or AnalyzerConfig()
        self._init_detectors()
        
        print(f"\n{'='*60}")
        print("✅ CodeSpectra Clone Analyzer v2.0")
        print(f"{'='*60}")
        print(f"   Structural threshold: {self.config.structural_threshold}")
        print(f"   Semantic threshold: {self.config.semantic_threshold}")
        print(f"   Simple problem ratio: {self.config.simple_problem_ratio}")
        print(f"{'='*60}\n")
    
    def _init_detectors(self):
        from detectors.type1.type1_detector import Type1Detector
        from detectors.type2.type2_detector import Type2Detector
        from detectors.type3.hybrid_detector import Type3HybridDetector
        from detectors.type4.type4_detector import Type4Detector

        self._type1      = Type1Detector()
        self._type2      = Type2Detector()
        self._structural = Type3HybridDetector(
            hybrid_threshold=self.config.structural_threshold,
            ml_threshold=self.config.ml_threshold,
        )
        self._semantic = Type4Detector(threshold=self.config.semantic_threshold)

    # =========================================================================
    # MAIN ANALYSIS METHODS
    # =========================================================================
    
    def analyze(
        self, 
        file_paths: List[str], 
        detailed: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze files for code similarity.
        
        Args:
            file_paths: List of file paths to analyze
            detailed: If True, include detailed breakdown (winnowing, AST, etc.)
                     If False, only include summary scores
        
        Returns:
            Complete analysis report as dictionary
        """
        start_time = time.time()
        n = len(file_paths)

        # Build same-language pairs FIRST so we report the true count
        same_lang_pairs = build_same_language_pairs(file_paths)
        total_comparisons = len(same_lang_pairs)

        print(f"📊 Analyzing {n} files ({total_comparisons} same-language pairs)...")
        print(f"   Mode: {'Detailed' if detailed else 'Summary'}")

        # Prepare detectors (frequency filter benefits from seeing all files)
        self._structural.prepare_batch([Path(p) for p in file_paths])
        self._semantic.clear_cache()

        # Analyze only same-language pairs (Type-1 through Type-4)
        pairs: List[PairResult] = []
        
        for file_a, file_b in same_lang_pairs:
            pair = self._analyze_pair(file_a, file_b, include_details=detailed)
            pairs.append(pair)
        
        # Class-wide analysis
        class_analysis = self._analyze_class(pairs)
        
        # Statistics
        stats = self._calculate_stats(pairs)
        
        # Get pairs needing review
        review_pairs = self._get_review_pairs(pairs, class_analysis)
        
        # Sort by highest similarity
        pairs.sort(
            key=lambda x: max(x.structural.score, x.semantic.score),
            reverse=True
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        # Build response
        return self._build_response(
            pairs=pairs,
            class_analysis=class_analysis,
            stats=stats,
            review_pairs=review_pairs,
            total_files=n,
            total_comparisons=total_comparisons,
            processing_time=processing_time,
            detailed=detailed
        )
    
    def get_pair_details(
        self, 
        file_path_a: str, 
        file_path_b: str
    ) -> Dict[str, Any]:
        """
        Get detailed analysis for a specific pair.
        
        Use this when user clicks "View Details" on frontend.
        
        Args:
            file_path_a: First file path
            file_path_b: Second file path
            
        Returns:
            Detailed analysis for this pair
        """
        print(f"🔍 Detailed analysis: {Path(file_path_a).name} vs {Path(file_path_b).name}")
        
        # Prepare detectors for single pair
        self._structural.prepare_batch([Path(file_path_a), Path(file_path_b)])
        self._semantic.clear_cache()
        
        # Analyze with full details
        pair = self._analyze_pair(file_path_a, file_path_b, include_details=True)
        
        return self._pair_to_dict(pair, detailed=True)
    
    # =========================================================================
    # PAIR ANALYSIS
    # =========================================================================
    
    def _analyze_pair(
        self, 
        file_a: str, 
        file_b: str,
        include_details: bool = False
    ) -> PairResult:
        """Analyze a single pair of files"""
        
        path_a = Path(file_a)
        path_b = Path(file_b)
        
        # ── Run Type-1 detection ──────────────────────────────────────────
        t1_result = self._type1.detect(file_a, file_b)
        t1_score  = t1_result.get("type1_score", 0.0)
        
        # ── Run Type-2 detection ──────────────────────────────────────────
        t2_result = self._type2.detect(file_a, file_b)
        t2_score  = t2_result.get("type2_score", 0.0)
        
        # ── Run structural (Type-3) analysis ──────────────────────────────
        structural = self._run_structural(path_a, path_b, include_details)
        
        # ── Run semantic (Type-4) analysis ────────────────────────────────
        semantic = self._run_semantic(file_a, file_b, include_details)
        
        # Determine similarity level
        level = self._get_similarity_level(structural, semantic)
        
        # Should review?
        needs_review = self._should_review(structural, semantic)
        
        # Generate summary
        summary = self._generate_summary(structural, semantic, level)
        
        return PairResult(
            file_a=path_a.name,
            file_b=path_b.name,
            structural=structural,
            semantic=semantic,
            similarity_level=level,
            needs_review=needs_review,
            summary=summary,
            type1_score=round(t1_score, 4),     # ← NOW POPULATED
            type2_score=round(t2_score, 4),      # ← NOW POPULATED
        )

    def _run_structural(
        self, 
        file_a: Path, 
        file_b: Path,
        include_details: bool
    ) -> StructuralResult:
        """Run structural (Type-3) analysis"""
        
        raw = self._structural.detect(file_a, file_b)
        
        hybrid = raw["hybrid"]
        ml = raw.get("ml")
        
        hybrid_score = hybrid["score"]
        ml_score = ml["score"] if ml else 0.0
        
        # Combined score (internal to structural)
        score = (hybrid_score * 0.5) + (ml_score * 0.5)
        
        # Is similar?
        is_similar = (hybrid_score >= self.config.structural_threshold) and \
                     (ml_score >= self.config.ml_threshold if ml else False)
        
        # Confidence
        confidence = self._get_confidence(score, 'structural')
        
        # Details (only if requested)
        details = None
        if include_details:
            details = StructuralDetails(
                winnowing_score=round(hybrid["details"]["winnowing_fingerprint_score"], 4),
                ast_score=round(hybrid["details"]["ast_skeleton_score"], 4),
                metrics_score=round(hybrid["details"]["complexity_metric_score"], 4),
                ml_score=round(ml_score, 4) if ml else None,
                hybrid_score=round(hybrid_score, 4)
            )
        
        return StructuralResult(
            score=round(score, 4),
            is_similar=is_similar,
            confidence=confidence,
            details=details
        )
    
    def _run_semantic(
        self, 
        file_a: str, 
        file_b: str,
        include_details: bool
    ) -> SemanticResult:
        """Run semantic (Type-4) analysis"""
        
        raw = self._semantic.detect(file_a, file_b, include_features=include_details)
        
        score = raw["semantic_score"]
        is_similar = raw["is_semantic_clone"]
        confidence = self._get_confidence(score, 'semantic')
        
        # Details (only if requested)
        details = None
        if include_details:
            categories = raw.get("category_scores", {})
            features_a = raw.get("features_a", {})
            features_b = raw.get("features_b", {})
            
            details = SemanticDetails(
                control_flow_score=round(categories.get("control_flow", 0), 4),
                data_flow_score=round(categories.get("data_flow", 0), 4),
                call_pattern_score=round(categories.get("call_pattern", 0), 4),
                structural_score=round(categories.get("structural", 0), 4),
                behavioral_score=round(categories.get("behavioral", 0), 4),
                behavioral_hash_a=features_a.get("behavioral_hash", ""),
                behavioral_hash_b=features_b.get("behavioral_hash", ""),
            )
        
        return SemanticResult(
            score=round(score, 4),
            is_similar=is_similar,
            confidence=confidence,
            details=details
        )
    
    def _get_confidence(self, score: float, analysis_type: str) -> str:
        """Get confidence level"""
        
        if analysis_type == 'structural':
            high = self.config.structural_high
            threshold = self.config.structural_threshold
        else:
            high = self.config.semantic_high
            threshold = self.config.semantic_threshold
        
        if score >= high:
            return 'HIGH'
        elif score >= threshold:
            return 'MEDIUM'
        elif score >= threshold * 0.8:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _get_similarity_level(
        self, 
        structural: StructuralResult, 
        semantic: SemanticResult
    ) -> str:
        """Get overall similarity level"""
        
        s_high = structural.confidence == 'HIGH'
        s_med = structural.confidence == 'MEDIUM'
        m_high = semantic.confidence == 'HIGH'
        m_med = semantic.confidence == 'MEDIUM'
        
        if s_high or m_high:
            return 'HIGH'
        elif s_med or m_med:
            return 'MEDIUM'
        elif structural.is_similar or semantic.is_similar:
            return 'LOW'
        else:
            return 'NONE'
    
    def _should_review(
        self, 
        structural: StructuralResult, 
        semantic: SemanticResult
    ) -> bool:
        """Should teacher review this pair?"""
        
        # Review if either HIGH
        if structural.confidence == 'HIGH' or semantic.confidence == 'HIGH':
            return True
        
        # Review if both MEDIUM
        if structural.confidence == 'MEDIUM' and semantic.confidence == 'MEDIUM':
            return True
        
        # Review if score exceeds threshold
        if structural.score >= self.config.review_threshold:
            return True
        if semantic.score >= self.config.review_threshold:
            return True
        
        return False
    
    def _generate_summary(
        self, 
        structural: StructuralResult, 
        semantic: SemanticResult,
        level: str
    ) -> str:
        """Generate human-readable summary"""
        
        s_pct = f"{structural.score:.0%}"
        m_pct = f"{semantic.score:.0%}"
        
        if level == 'HIGH':
            if structural.confidence == 'HIGH' and semantic.confidence == 'HIGH':
                return f"High similarity: structural {s_pct}, semantic {m_pct}. Both analyses agree. Review recommended."
            elif structural.confidence == 'HIGH':
                return f"High structural similarity ({s_pct}). Code structure is very similar."
            else:
                return f"High semantic similarity ({m_pct}). Code behaves similarly despite different structure."
        
        elif level == 'MEDIUM':
            return f"Moderate similarity: structural {s_pct}, semantic {m_pct}."
        
        elif level == 'LOW':
            return f"Low similarity: structural {s_pct}, semantic {m_pct}."
        
        else:
            return f"Minimal similarity: structural {s_pct}, semantic {m_pct}."
    
    # =========================================================================
    # CLASS-WIDE ANALYSIS
    # =========================================================================
    
    def _analyze_class(self, pairs: List[PairResult]) -> ClassAnalysis:
        """Analyze class-wide patterns"""
        
        if not pairs:
            return ClassAnalysis(
                is_simple_problem=False,
                high_similarity_ratio=0.0,
                average_structural=0.0,
                average_semantic=0.0,
                message="No pairs to analyze.",
                outlier_pairs=[]
            )
        
        total = len(pairs)
        
        # Averages
        avg_structural = sum(p.structural.score for p in pairs) / total
        avg_semantic = sum(p.semantic.score for p in pairs) / total
        
        # High similarity count
        threshold = self.config.class_high_similarity_threshold
        high_count = sum(
            1 for p in pairs
            if p.structural.score >= threshold or p.semantic.score >= threshold
        )
        
        high_ratio = high_count / total
        is_simple = high_ratio >= self.config.simple_problem_ratio
        
        # Find outliers (significantly above average)
        outlier_threshold_s = avg_structural + 0.15
        outlier_threshold_m = avg_semantic + 0.15
        
        outliers = [
            {
                "file_a": p.file_a,
                "file_b": p.file_b,
                "structural_score": p.structural.score,
                "semantic_score": p.semantic.score,
                "above_avg_structural": round(p.structural.score - avg_structural, 4),
                "above_avg_semantic": round(p.semantic.score - avg_semantic, 4),
            }
            for p in pairs
            if p.structural.score >= outlier_threshold_s or p.semantic.score >= outlier_threshold_m
        ]
        
        outliers.sort(
            key=lambda x: max(x["structural_score"], x["semantic_score"]),
            reverse=True
        )
        
        # Message
        if is_simple:
            message = (
                f"📋 SIMPLE PROBLEM DETECTED: {high_ratio:.0%} of pairs have high similarity "
                f"(>{threshold:.0%}). This is likely a standard problem where similar "
                f"solutions are expected. Focus on {len(outliers)} outlier pair(s) that are "
                f"significantly above average (structural avg: {avg_structural:.0%}, "
                f"semantic avg: {avg_semantic:.0%})."
            )
        elif high_ratio > 0.3:
            message = (
                f"⚠️ ELEVATED SIMILARITY: {high_ratio:.0%} of pairs have high similarity. "
                f"Review flagged pairs carefully."
            )
        else:
            message = (
                f"✅ NORMAL PATTERN: {high_ratio:.0%} of pairs have high similarity. "
                f"This is within expected range."
            )
        
        return ClassAnalysis(
            is_simple_problem=is_simple,
            high_similarity_ratio=round(high_ratio, 4),
            average_structural=round(avg_structural, 4),
            average_semantic=round(avg_semantic, 4),
            message=message,
            outlier_pairs=outliers[:10]
        )
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def _calculate_stats(self, pairs: List[PairResult]) -> Dict:
        """Calculate statistics"""
        
        return {
            "structural": {
                "high": sum(1 for p in pairs if p.structural.confidence == 'HIGH'),
                "medium": sum(1 for p in pairs if p.structural.confidence == 'MEDIUM'),
                "low": sum(1 for p in pairs if p.structural.confidence == 'LOW'),
                "similar_count": sum(1 for p in pairs if p.structural.is_similar),
            },
            "semantic": {
                "high": sum(1 for p in pairs if p.semantic.confidence == 'HIGH'),
                "medium": sum(1 for p in pairs if p.semantic.confidence == 'MEDIUM'),
                "low": sum(1 for p in pairs if p.semantic.confidence == 'LOW'),
                "similar_count": sum(1 for p in pairs if p.semantic.is_similar),
            },
            "overall": {
                "high_similarity": sum(1 for p in pairs if p.similarity_level == 'HIGH'),
                "medium_similarity": sum(1 for p in pairs if p.similarity_level == 'MEDIUM'),
                "low_similarity": sum(1 for p in pairs if p.similarity_level == 'LOW'),
                "needs_review": sum(1 for p in pairs if p.needs_review),
            }
        }
    
    def _get_review_pairs(
        self, 
        pairs: List[PairResult],
        class_analysis: ClassAnalysis
    ) -> List[Dict]:
        """Get pairs that need teacher review"""
        
        review = []
        
        for p in pairs:
            if p.needs_review:
                is_outlier = (
                    p.structural.score >= class_analysis.average_structural + 0.15 or
                    p.semantic.score >= class_analysis.average_semantic + 0.15
                )
                
                review.append({
                    "file_a": p.file_a,
                    "file_b": p.file_b,
                    "structural_score": p.structural.score,
                    "structural_confidence": p.structural.confidence,
                    "semantic_score": p.semantic.score,
                    "semantic_confidence": p.semantic.confidence,
                    "similarity_level": p.similarity_level,
                    "is_outlier": is_outlier,
                    "summary": p.summary,
                })
        
        review.sort(
            key=lambda x: max(x["structural_score"], x["semantic_score"]),
            reverse=True
        )
        
        return review
    
    # =========================================================================
    # RESPONSE BUILDING
    # =========================================================================
    
    def _build_response(
        self,
        pairs: List[PairResult],
        class_analysis: ClassAnalysis,
        stats: Dict,
        review_pairs: List[Dict],
        total_files: int,
        total_comparisons: int,
        processing_time: float,
        detailed: bool
    ) -> Dict[str, Any]:
        """Build the final response dictionary"""
        
        return {
            "metadata": {
                "total_files": total_files,
                "total_comparisons": total_comparisons,
                "processing_time_ms": round(processing_time, 2),
                "analysis_mode": "detailed" if detailed else "summary",
            },
            
            "class_analysis": {
                "is_simple_problem": class_analysis.is_simple_problem,
                "high_similarity_ratio": class_analysis.high_similarity_ratio,
                "average_structural_similarity": class_analysis.average_structural,
                "average_semantic_similarity": class_analysis.average_semantic,
                "message": class_analysis.message,
                "outlier_pairs": class_analysis.outlier_pairs,
            },
            
            "statistics": stats,
            
            "pairs_needing_review": review_pairs,
            
            "all_pairs": [
                self._pair_to_dict(p, detailed) for p in pairs
            ],
        }
    
    def _pair_to_dict(self, pair: PairResult, detailed: bool) -> Dict:
        """Convert PairResult to dictionary"""
        
        result = {
            "file_a": pair.file_a,
            "file_b": pair.file_b,
            
            # ── Type-1 & Type-2 scores (NEW — was missing!) ───────────────
            "type1_score": pair.type1_score,
            "type2_score": pair.type2_score,
            
            "structural": {
                "score": pair.structural.score,
                "confidence": pair.structural.confidence,
                "is_similar": pair.structural.is_similar,
            },
            
            "semantic": {
                "score": pair.semantic.score,
                "confidence": pair.semantic.confidence,
                "is_similar": pair.semantic.is_similar,
            },
            
            "similarity_level": pair.similarity_level,
            "needs_review": pair.needs_review,
            "summary": pair.summary,
        }
        
        # Add details if available and requested
        if detailed:
            if pair.structural.details:
                result["structural"]["details"] = {
                    "winnowing_score": pair.structural.details.winnowing_score,
                    "ast_score": pair.structural.details.ast_score,
                    "metrics_score": pair.structural.details.metrics_score,
                    "ml_score": pair.structural.details.ml_score,
                    "hybrid_score": pair.structural.details.hybrid_score,
                }
            
            if pair.semantic.details:
                result["semantic"]["details"] = {
                    "control_flow_score": pair.semantic.details.control_flow_score,
                    "data_flow_score": pair.semantic.details.data_flow_score,
                    "call_pattern_score": pair.semantic.details.call_pattern_score,
                    "structural_score": pair.semantic.details.structural_score,
                    "behavioral_score": pair.semantic.details.behavioral_score,
                    "behavioral_hash_a": pair.semantic.details.behavioral_hash_a,
                    "behavioral_hash_b": pair.semantic.details.behavioral_hash_b,
                }
        
        return result

# =============================================================================
# QUESTION-AWARE CROSS-STUDENT ANALYSIS  (v2.1 addition)
# =============================================================================

import concurrent.futures as _cf


def _analyze_for_assignment(
    self,
    student_submissions: list,
    language: str = "cpp",
    extension_weights: dict = None,
    pair_timeout_seconds: int = 30,
    skip_pairs: set = None,
) -> dict:
    """
    Cross-student comparison for one assignment question.

    Args:
        student_submissions: list of {student_id, submission_id, files:[abs_paths]}
        language:            primary language string
        extension_weights:   override weights, e.g. {".h": 0.4}
        pair_timeout_seconds: max seconds per pair before it's queued for retry
        skip_pairs:          set of (i,j) tuples already processed (for retry)

    Returns dict with keys:
        status, analyzed_count, total_pairs,
        remaining_pairs, clone_pairs, class_analysis
    """
    n           = len(student_submissions)
    skip_pairs  = skip_pairs or set()

    # Prepare batch frequency filter across ALL students' files
    all_files = [f for sub in student_submissions for f in sub["files"]]
    self._structural.prepare_batch([Path(p) for p in all_files])
    self._semantic.clear_cache()

    # Build same-language cross-student pairs.
    # For each student pair (i, j), we compare only files of the same language.
    # build_same_language_pairs is called per-student-pair to stay cross-student.
    student_pairs = [(i, j) for i in range(n) for j in range(i+1, n)
                     if (i, j) not in skip_pairs]
    total_pairs = len(student_pairs)

    clone_pairs:     list = []
    remaining_pairs: list = []
    analyzed_count:  int  = 0

    for i, j in student_pairs:
            sub_a = student_submissions[i]
            sub_b = student_submissions[j]

            best_result = None
            with _cf.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(_compare_student_pair, self, sub_a, sub_b)
                try:
                    best_result    = future.result(timeout=pair_timeout_seconds)
                    analyzed_count += 1
                except _cf.TimeoutError:
                    print(f"⏱  Pair ({i},{j}) timed out — queued")
                    remaining_pairs.append([i, j])
                    continue
                except Exception as e:
                    print(f"⚠️  Pair ({i},{j}) error: {e} — queued")
                    remaining_pairs.append([i, j])
                    continue

            if best_result and (
                best_result["is_clone"] or
                best_result["confidence"] in ("HIGH", "MEDIUM")
            ):
                clone_pairs.append({
                    "student_a_id":    sub_a["student_id"],
                    "submission_a_id": sub_a["submission_id"],
                    "student_b_id":    sub_b["student_id"],
                    "submission_b_id": sub_b["submission_id"],
                    "structural_score": best_result["structural_score"],
                    "semantic_score":   best_result["semantic_score"],
                    "combined_score":   best_result["combined_score"],
                    "confidence":       best_result["confidence"],
                    "is_clone":         best_result["is_clone"],
                    "file_a":           best_result["file_a"],
                    "file_b":           best_result["file_b"],
                    "details":          best_result.get("details", {}),
                })

    scores    = [p["combined_score"] for p in clone_pairs]
    avg_score = sum(scores) / len(scores) if scores else 0.0

    return {
        "status":          "complete" if not remaining_pairs else "partial",
        "analyzed_count":  analyzed_count,
        "total_pairs":     total_pairs,
        "remaining_pairs": remaining_pairs,
        "clone_pairs":     clone_pairs,
        "class_analysis": {
            "total_students":     n,
            "total_pairs":        total_pairs,
            "analyzed_pairs":     analyzed_count,
            "clone_pairs_found":  len(clone_pairs),
            "high_confidence":    sum(1 for p in clone_pairs if p["confidence"] == "HIGH"),
            "average_similarity": round(avg_score, 4),
        },
    }


def _compare_student_pair(self, sub_a: dict, sub_b: dict) -> dict:
    """Compare two student submissions — only same-language file pairs."""
    best = None
    # Build same-language pairs across the two students' file lists
    combined = sub_a["files"] + sub_b["files"]
    a_set    = set(sub_a["files"])
    b_set    = set(sub_b["files"])
    lang_pairs = [
        (fa, fb)
        for fa, fb in build_same_language_pairs(combined)
        if (fa in a_set and fb in b_set) or (fb in a_set and fa in b_set)
    ]
    for fa, fb in lang_pairs:
        # Keep fa from student_a, fb from student_b
        if fa not in a_set:
            fa, fb = fb, fa
        try:
            t1 = self._type1.detect(fa, fb)
            t2 = self._type2.detect(fa, fb)
            struct   = self._run_structural(Path(fa), Path(fb), include_details=True)
            semantic = self._run_semantic(fa, fb, include_details=False)
            pair_combined = (struct.score + semantic.score) / 2
            confidence = (
                "HIGH"     if pair_combined >= 0.70 else
                "MEDIUM"   if pair_combined >= 0.50 else
                "LOW"      if pair_combined >= 0.35 else
                "UNLIKELY"
            )
            candidate = {
                "file_a":            fa,
                "file_b":            fb,
                "type1_score":       t1.get("type1_score", 0.0),
                "type2_score":       t2.get("type2_score", 0.0),
                "structural_score":  struct.score,
                "semantic_score":    semantic.score,
                "combined_score":    round(pair_combined, 4),
                "confidence":        confidence,
                "is_clone":          pair_combined >= self.config.review_threshold,
                "details":           {"structural": vars(struct.details) if struct.details else {}},
            }
            if best is None or pair_combined > best["combined_score"]:
                best = candidate
        except Exception as e:
            print(f"  ⚠️  {Path(fa).name} vs {Path(fb).name}: {e}")
    return best

# Attach new methods to CloneAnalyzer
CloneAnalyzer.analyze_for_assignment = _analyze_for_assignment
CloneAnalyzer._compare_student_pair  = _compare_student_pair


# =============================================================================
# LANGUAGE-AWARE FILE GROUPING  (shared utility for all detector types)
# =============================================================================

# Maps file extension → canonical language name.
# Same-language files are compared together; cross-language pairs are SKIPPED
# by ALL detectors (Type-1 through Type-4).
LANG_EXT_MAP: Dict[str, str] = {
    # C / C++
    ".c": "cpp", ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".h": "cpp", ".hpp": "cpp",
    # Java
    ".java": "java",
    # Python
    ".py": "python",
    # JavaScript / TypeScript (treated as one pool)
    ".js": "javascript", ".jsx": "javascript",
    ".ts": "javascript", ".tsx": "javascript",
}


def group_files_by_language(file_paths: List[str]) -> Dict[str, List[str]]:
    """
    Group a flat list of file paths by their programming language.

    Returns a dict like::

        {
            "cpp":        ["/path/to/main.cpp", "/path/to/utils.h"],
            "java":       ["/path/to/Solution.java"],
            "javascript": ["/path/to/frontend/App.jsx", "/path/to/backend/server.js"],
        }

    Files with unrecognised extensions are silently dropped — they cannot be
    compared meaningfully by any of the four detectors.

    Design rationale
    ----------------
    Both NiCad and PMD/CPD group by language before comparison.  Comparing
    a Python file against a C++ file would produce meaningless scores because:
    - Tokens differ (keywords, syntax)
    - AST structure is completely different
    - Semantic PDG edges have no correspondence
    This grouping is therefore enforced *before* any detector runs.
    """
    groups: Dict[str, List[str]] = {}
    for fp in file_paths:
        ext  = Path(fp).suffix.lower()
        lang = LANG_EXT_MAP.get(ext)
        if lang:
            groups.setdefault(lang, []).append(fp)
    return groups


def build_same_language_pairs(file_paths: List[str]) -> List[Tuple[str, str]]:
    """
    Return all (file_a, file_b) pairs where both files share the same language.

    Used by CloneAnalyzer.analyze() and detect_batch() in UnifiedDetector so
    all four detector types automatically skip cross-language comparisons.
    """
    from itertools import combinations
    pairs: List[Tuple[str, str]] = []
    for lang_files in group_files_by_language(file_paths).values():
        pairs.extend(combinations(lang_files, 2))
    return pairs