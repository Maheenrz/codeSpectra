# analysis-engine/engine/analyzer.py

"""
CodeSpectra Clone Analyzer v2.1 — FIXED
========================================

Fixes:
  1. _run_structural no longer uses AND logic for is_similar
  2. ML fallback: if ML not available, use hybrid_score alone (not 50/50 with 0)
  3. _pair_to_dict now includes type1_score, type2_score, AND primary_clone_type
  4. clone_type_discrimination from fragment_comparator is propagated
  5. Primary clone type determination based on all 4 scores
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
    discrimination: Optional[Dict] = None    # ← NEW: type1/2/3/none counts


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
    primary_clone_type: str = "none"   # ← NEW: "type1", "type2", "type3", "type4", "none"


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
# HELPER: same-language pairing
# =============================================================================

_EXT_LANG = {
    ".java": "java",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".c": "c", ".h": "cpp", ".hpp": "cpp",
    ".py": "python",
    ".js": "javascript", ".ts": "javascript",
    ".jsx": "javascript", ".tsx": "javascript",
}


def _get_lang(path: str) -> str:
    return _EXT_LANG.get(Path(path).suffix.lower(), "unknown")


def build_same_language_pairs(file_paths: List[str]) -> List[Tuple[str, str]]:
    """Only pair files that share the same language."""
    pairs = []
    n = len(file_paths)
    for i in range(n):
        for j in range(i + 1, n):
            if _get_lang(file_paths[i]) == _get_lang(file_paths[j]):
                pairs.append((file_paths[i], file_paths[j]))
    return pairs


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
        print("✅ CodeSpectra Clone Analyzer v2.1 (FIXED)")
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
        start_time = time.time()
        n = len(file_paths)

        same_lang_pairs = build_same_language_pairs(file_paths)
        total_comparisons = len(same_lang_pairs)

        print(f"📊 Analyzing {n} files ({total_comparisons} same-language pairs)...")
        print(f"   Mode: {'Detailed' if detailed else 'Summary'}")

        self._structural.prepare_batch([Path(p) for p in file_paths])
        self._semantic.clear_cache()

        pairs: List[PairResult] = []
        
        for file_a, file_b in same_lang_pairs:
            pair = self._analyze_pair(file_a, file_b, include_details=detailed)
            pairs.append(pair)
        
        class_analysis = self._analyze_class(pairs)
        stats = self._calculate_stats(pairs)
        review_pairs = self._get_review_pairs(pairs, class_analysis)
        
        pairs.sort(
            key=lambda x: max(x.structural.score, x.semantic.score),
            reverse=True
        )
        
        processing_time = (time.time() - start_time) * 1000
        
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

    def analyze_for_assignment(
        self,
        student_submissions: List[Dict],
        language: str = "cpp",
        extension_weights: Dict[str, float] = None,
        pair_timeout_seconds: int = 30,
        skip_pairs: set = None,
    ) -> Dict[str, Any]:
        """
        Cross-student analysis for assignment mode.
        Each submission dict has: student_id, submission_id, files (list of paths).
        """
        import signal
        skip_pairs = skip_pairs or set()
        n = len(student_submissions)

        # Collect all files for batch prep
        all_files = []
        for sub in student_submissions:
            all_files.extend(sub.get("files", []))

        self._structural.prepare_batch([Path(p) for p in all_files])
        self._semantic.clear_cache()

        clone_pairs = []
        remaining_pairs = []

        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) in skip_pairs:
                    continue

                sub_a = student_submissions[i]
                sub_b = student_submissions[j]

                try:
                    # Compare all file pairs between two students
                    best_pair = None
                    best_score = 0.0

                    for fa in sub_a.get("files", []):
                        for fb in sub_b.get("files", []):
                            if not Path(fa).exists() or not Path(fb).exists():
                                continue
                            if _get_lang(fa) != _get_lang(fb):
                                continue

                            pair = self._analyze_pair(fa, fb, include_details=False)
                            overall = max(pair.structural.score, pair.semantic.score)

                            if overall > best_score:
                                best_score = overall
                                best_pair = pair

                    if best_pair and best_score >= 0.40:
                        clone_pairs.append({
                            "student_a_id": sub_a.get("student_id"),
                            "student_b_id": sub_b.get("student_id"),
                            "submission_a_id": sub_a.get("submission_id"),
                            "submission_b_id": sub_b.get("submission_id"),
                            "file_a": best_pair.file_a,
                            "file_b": best_pair.file_b,
                            "type1_score": best_pair.type1_score,
                            "type2_score": best_pair.type2_score,
                            "structural_score": best_pair.structural.score,
                            "semantic_score": best_pair.semantic.score,
                            "primary_clone_type": best_pair.primary_clone_type,
                            "similarity_level": best_pair.similarity_level,
                            "needs_review": best_pair.needs_review,
                            "summary": best_pair.summary,
                        })

                except Exception as e:
                    print(f"⚠️ Pair ({i},{j}) error: {e}")
                    remaining_pairs.append([i, j])

        return {
            "clone_pairs": clone_pairs,
            "remaining_pairs": remaining_pairs,
            "class_analysis": {},
        }
    
    def get_pair_details(
        self, 
        file_path_a: str, 
        file_path_b: str
    ) -> Dict[str, Any]:
        print(f"🔍 Detailed analysis: {Path(file_path_a).name} vs {Path(file_path_b).name}")
        
        self._structural.prepare_batch([Path(file_path_a), Path(file_path_b)])
        self._semantic.clear_cache()
        
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
        
        # ── Determine PRIMARY clone type ──────────────────────────────────
        # This is THE KEY FIX: use all 4 scores to determine what kind
        # of clone this actually is, using standard research definitions.
        primary_clone_type = self._determine_primary_clone_type(
            t1_score, t2_score, structural.score, semantic.score
        )
        
        # Determine similarity level
        level = self._get_similarity_level(structural, semantic)
        
        # Should review?
        needs_review = self._should_review(structural, semantic)
        
        # Generate summary
        summary = self._generate_summary(structural, semantic, level, primary_clone_type)
        
        return PairResult(
            file_a=path_a.name,
            file_b=path_b.name,
            structural=structural,
            semantic=semantic,
            similarity_level=level,
            needs_review=needs_review,
            summary=summary,
            type1_score=round(t1_score, 4),
            type2_score=round(t2_score, 4),
            primary_clone_type=primary_clone_type,
        )

    def _determine_primary_clone_type(
        self,
        type1_score: float,
        type2_score: float,
        structural_score: float,
        semantic_score: float,
    ) -> str:
        """
        Determine the PRIMARY clone type based on all 4 detector scores.
        
        Research-based classification (Roy & Cordy 2007, Bellon et al. 2007):
        
          Type-1 (Exact):     Identical code ignoring whitespace/comments
                              → type1_score >= 0.95
          
          Type-2 (Renamed):   Same structure, only identifiers/literals renamed
                              → type2_score >= 0.80 AND type1_score < 0.95
          
          Type-3 (Near-miss): Structural modifications (added/deleted/changed
                              statements) beyond just renaming
                              → structural_score >= 0.50 AND type2_score < 0.80
          
          Type-4 (Semantic):  Different implementation, same behavior
                              → semantic_score >= 0.60 AND structural_score < 0.50
        
        Priority: Type-1 > Type-2 > Type-3 > Type-4 > none
        (A Type-1 clone is trivially also a Type-2 and Type-3, so we
         report the MOST SPECIFIC type.)
        """
        # Type-1: exact copy
        if type1_score >= 0.95:
            return "type1"
        
        # Type-2: renamed variables/identifiers but same structure
        if type2_score >= 0.80:
            return "type2"
        
        # Type-3: structural modifications beyond renaming
        if structural_score >= 0.50:
            return "type3"
        
        # Type-4: semantically similar but structurally different
        if semantic_score >= 0.60:
            return "type4"
        
        return "none"

    def _run_structural(
        self, 
        file_a: Path, 
        file_b: Path,
        include_details: bool
    ) -> StructuralResult:
        """
        Run structural (Type-3) analysis.
        
        FIXES:
          1. No longer uses AND logic — hybrid alone is sufficient
          2. If ML unavailable, score = hybrid (not hybrid*0.5 + 0*0.5)
          3. Propagates discrimination data (type1/2/3 fragment counts)
        """
        
        raw = self._structural.detect(file_a, file_b)
        
        hybrid = raw["hybrid"]
        ml = raw.get("ml")
        
        hybrid_score = hybrid["score"]
        ml_score = ml["score"] if ml else None
        
        # ── FIX #1: Score calculation ─────────────────────────────────────
        # OLD (broken): score = (hybrid_score * 0.5) + (ml_score * 0.5)
        #   → When ML=None, score = hybrid*0.5 + 0*0.5 = half the real score!
        # NEW: If ML available, blend. If not, use hybrid alone.
        if ml_score is not None:
            score = (hybrid_score * 0.6) + (ml_score * 0.4)
        else:
            score = hybrid_score
        
        # ── FIX #2: is_similar — OR logic, not AND ───────────────────────��
        # OLD (broken): hybrid >= threshold AND ml >= threshold
        #   → If ML unavailable, ALWAYS False!
        # NEW: hybrid alone is enough; ML just adds confidence
        is_similar = hybrid_score >= self.config.structural_threshold
        if ml_score is not None:
            # If ML disagrees strongly, downgrade
            if ml_score < 0.30 and hybrid_score < self.config.structural_high:
                is_similar = False
        
        # Confidence
        confidence = self._get_confidence(score, 'structural')
        
        # ── FIX #3: Extract discrimination data ──────────────────────────
        discrimination = raw.get("clone_type_discrimination", {})
        
        # Details (only if requested)
        details = None
        if include_details:
            detail_data = hybrid.get("details", {})
            details = StructuralDetails(
                winnowing_score=round(detail_data.get("winnowing_fingerprint_score", 0.0), 4),
                ast_score=round(detail_data.get("ast_skeleton_score", 0.0), 4),
                metrics_score=round(detail_data.get("complexity_metric_score", 0.0), 4),
                ml_score=round(ml_score, 4) if ml_score is not None else None,
                hybrid_score=round(hybrid_score, 4)
            )
        
        return StructuralResult(
            score=round(score, 4),
            is_similar=is_similar,
            confidence=confidence,
            details=details,
            discrimination=discrimination,
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
            if score >= self.config.structural_high + 0.15:
                return 'CRITICAL'
            elif score >= self.config.structural_high:
                return 'HIGH'
            elif score >= self.config.structural_threshold:
                return 'MEDIUM'
            elif score >= 0.35:
                return 'LOW'
            else:
                return 'UNLIKELY'
        else:  # semantic
            if score >= self.config.semantic_high + 0.10:
                return 'CRITICAL'
            elif score >= self.config.semantic_high:
                return 'HIGH'
            elif score >= self.config.semantic_threshold:
                return 'MEDIUM'
            elif score >= 0.40:
                return 'LOW'
            else:
                return 'UNLIKELY'
    
    def _get_similarity_level(
        self, 
        structural: StructuralResult, 
        semantic: SemanticResult
    ) -> str:
        """Get overall similarity level"""
        max_score = max(structural.score, semantic.score)
        
        if max_score >= 0.85:
            return 'CRITICAL'
        elif max_score >= 0.70:
            return 'HIGH'
        elif max_score >= 0.50:
            return 'MEDIUM'
        elif max_score >= 0.35:
            return 'LOW'
        else:
            return 'NONE'
    
    def _should_review(
        self, 
        structural: StructuralResult, 
        semantic: SemanticResult
    ) -> bool:
        """Should teacher review this pair?"""
        max_score = max(structural.score, semantic.score)
        return max_score >= self.config.review_threshold
    
    def _generate_summary(
        self, 
        structural: StructuralResult, 
        semantic: SemanticResult,
        level: str,
        primary_clone_type: str = "none"
    ) -> str:
        """Generate human-readable summary"""
        
        type_labels = {
            "type1": "Type-1 (Exact Copy)",
            "type2": "Type-2 (Renamed Variables)",
            "type3": "Type-3 (Structural Clone)",
            "type4": "Type-4 (Semantic Clone)",
            "none":  "No significant clone detected",
        }
        
        clone_label = type_labels.get(primary_clone_type, "Unknown")
        
        if level in ('CRITICAL', 'HIGH'):
            return f"⚠️ {clone_label} — Structural: {structural.score:.0%}, Semantic: {semantic.score:.0%}. Needs review."
        elif level == 'MEDIUM':
            return f"📋 {clone_label} — Structural: {structural.score:.0%}, Semantic: {semantic.score:.0%}. Consider reviewing."
        elif level == 'LOW':
            return f"ℹ️ Low similarity — Structural: {structural.score:.0%}, Semantic: {semantic.score:.0%}."
        else:
            return f"✅ No significant similarity detected."
    
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
                message="No pairs to analyze",
                outlier_pairs=[]
            )
        
        avg_structural = sum(p.structural.score for p in pairs) / len(pairs)
        avg_semantic = sum(p.semantic.score for p in pairs) / len(pairs)
        
        high_count = sum(
            1 for p in pairs
            if p.structural.score >= self.config.class_high_similarity_threshold
            or p.semantic.score >= self.config.class_high_similarity_threshold
        )
        high_ratio = high_count / len(pairs) if pairs else 0
        
        is_simple = high_ratio >= self.config.simple_problem_ratio
        
        # Find outliers (pairs significantly above average)
        outliers = []
        for p in pairs:
            if (p.structural.score >= avg_structural + 0.20 or
                p.semantic.score >= avg_semantic + 0.20):
                outliers.append({
                    "file_a": p.file_a,
                    "file_b": p.file_b,
                    "structural_score": p.structural.score,
                    "semantic_score": p.semantic.score,
                    "primary_clone_type": p.primary_clone_type,
                })
        
        if is_simple:
            message = (
                f"⚠️ Simple problem detected: {high_ratio:.0%} of pairs show high similarity. "
                f"This may be expected for this type of assignment."
            )
        elif high_count > 0:
            message = f"📋 {high_count} pair(s) show high similarity and need review."
        else:
            message = "✅ No concerning patterns detected."
        
        return ClassAnalysis(
            is_simple_problem=is_simple,
            high_similarity_ratio=round(high_ratio, 4),
            average_structural=round(avg_structural, 4),
            average_semantic=round(avg_semantic, 4),
            message=message,
            outlier_pairs=outliers
        )
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def _calculate_stats(self, pairs: List[PairResult]) -> Dict:
        """Calculate statistics"""
        
        return {
            "structural": {
                "high": sum(1 for p in pairs if p.structural.confidence in ('HIGH', 'CRITICAL')),
                "medium": sum(1 for p in pairs if p.structural.confidence == 'MEDIUM'),
                "low": sum(1 for p in pairs if p.structural.confidence == 'LOW'),
                "similar_count": sum(1 for p in pairs if p.structural.is_similar),
            },
            "semantic": {
                "high": sum(1 for p in pairs if p.semantic.confidence in ('HIGH', 'CRITICAL')),
                "medium": sum(1 for p in pairs if p.semantic.confidence == 'MEDIUM'),
                "low": sum(1 for p in pairs if p.semantic.confidence == 'LOW'),
                "similar_count": sum(1 for p in pairs if p.semantic.is_similar),
            },
            "clone_types": {
                "type1": sum(1 for p in pairs if p.primary_clone_type == "type1"),
                "type2": sum(1 for p in pairs if p.primary_clone_type == "type2"),
                "type3": sum(1 for p in pairs if p.primary_clone_type == "type3"),
                "type4": sum(1 for p in pairs if p.primary_clone_type == "type4"),
                "none":  sum(1 for p in pairs if p.primary_clone_type == "none"),
            },
            "overall": {
                "high_similarity": sum(1 for p in pairs if p.similarity_level in ('HIGH', 'CRITICAL')),
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
                    "type1_score": p.type1_score,
                    "type2_score": p.type2_score,
                    "structural_score": p.structural.score,
                    "structural_confidence": p.structural.confidence,
                    "semantic_score": p.semantic.score,
                    "semantic_confidence": p.semantic.confidence,
                    "primary_clone_type": p.primary_clone_type,
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
        """
        Convert PairResult to dictionary.
        
        FIX: Now includes type1_score, type2_score, primary_clone_type,
        and discrimination data — all of which were missing before.
        """
        
        result = {
            "file_a": pair.file_a,
            "file_b": pair.file_b,
            
            # ── NEW: All 4 type scores at top level ──────────────────────
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
            
            # ── NEW: Primary clone type determination ────────────────────
            "primary_clone_type": pair.primary_clone_type,
            
            "similarity_level": pair.similarity_level,
            "needs_review": pair.needs_review,
            "summary": pair.summary,
        }
        
        # Add discrimination data if available
        if pair.structural.discrimination:
            result["clone_type_discrimination"] = pair.structural.discrimination
        
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