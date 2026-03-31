# analysis-engine/engine/analyzer.py

"""
CodeSpectra Clone Analyzer v3.1
================================

v3.1 adds: Cross-Layer / IoT Analysis (on top of v3.0)
  - Automatically detects multi-tier codebases (watch → phone → cloud)
  - Bridges the REST ↔ JS naming gap via canonical token normalization
  - Zero overhead for regular student assignments (gated by a batch-level scan)
  - Results surface as 'cross_layer' key in every pair's JSON output

v3.0 changes (on top of v2.4):
  1. Type-4 ENABLED with the new Educational Pipeline:
       - AlgorithmClassifier  (static signature, problem category)
       - IOBehavioralTester   (compile + run student code, compare outputs)
       - JoernDetector PDG    (WL-kernel graph similarity, if Docker up)
       - ScoreFusion          (pdg×0.35 + io×0.45 + signature×0.20)
  2. Type-4 pre-filter: only runs when T1/T2/T3 combined score < 0.50
     (prevents wasting time on obvious text clones)
  3. type2 threshold kept at 0.65 (v2.4 value)
  4. type4 threshold set to 0.60 (educational calibrated)
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import time
import sys
import math
import gc

try:
    import psutil
except ImportError:
    psutil = None

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Cross-layer / IoT detector — the new addition in v3.1.
# We import lazily inside methods so a missing dependency never breaks
# the regular student-assignment flow.
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
# CONFIGURATION
# =============================================================================

@dataclass
class AnalyzerConfig:
    structural_threshold: float = 0.50
    structural_high: float = 0.70
    ml_threshold: float = 0.60
    semantic_threshold: float = 0.60
    semantic_high: float = 0.80
    class_high_similarity_threshold: float = 0.70
    simple_problem_ratio: float = 0.70
    review_threshold: float = 0.70
    type1_threshold: float = 0.98
    type2_threshold: float = 0.90


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class StructuralDetails:
    winnowing_score: float
    ast_score: float
    metrics_score: float
    ml_score: Optional[float]
    hybrid_score: float


@dataclass
class SemanticDetails:
    control_flow_score: float
    data_flow_score: float
    call_pattern_score: float
    structural_score: float
    behavioral_score: float
    behavioral_hash_a: str
    behavioral_hash_b: str


@dataclass
class StructuralResult:
    score: float
    is_similar: bool
    confidence: str
    details: Optional[StructuralDetails] = None
    discrimination: Optional[Dict] = None
    all_type3_pairs: Optional[List] = None


@dataclass
class SemanticResult:
    score: float
    is_similar: bool
    confidence: str
    details: Optional[SemanticDetails] = None
    io_match_score: Optional[float] = None
    io_available: bool = False
    interpretation: str = ""


@dataclass
class PairResult:
    file_a: str
    file_b: str
    structural: StructuralResult
    semantic: SemanticResult
    similarity_level: str
    needs_review: bool
    summary: str
    type1_score: float = 0.0
    type2_score: float = 0.0
    primary_clone_type: str = "none"
    # v3.1 — cross-layer result, None when not applicable (student C++/Java/Python, etc.)
    cross_layer: Optional[Any] = None


# =============================================================================
# HELPERS
# =============================================================================

_EXT_LANG = {
    ".java": "java",
    ".kt":   "java",    # Kotlin — paired with Java for clone detection
    ".kts":  "java",    # Kotlin Script
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".c": "c", ".h": "cpp", ".hpp": "cpp",
    ".py": "python",
    ".js": "javascript", ".ts": "javascript",
    ".jsx": "javascript", ".tsx": "javascript",
}


def _get_lang(path: str) -> str:
    return _EXT_LANG.get(Path(path).suffix.lower(), "unknown")


def build_same_language_pairs(file_paths: List[str]) -> List[Tuple[str, str]]:
    pairs = []
    n = len(file_paths)
    for i in range(n):
        for j in range(i + 1, n):
            if _get_lang(file_paths[i]) == _get_lang(file_paths[j]):
                pairs.append((file_paths[i], file_paths[j]))
    return pairs


def _build_all_pairs(file_paths: List[str]) -> List[Tuple[str, str]]:
    """
    For cross-layer analysis we intentionally pair files across languages too
    (e.g. a .js watch file paired with a .txt REST spec). This is separate
    from the regular same-language pairing used by the clone detectors.
    """
    pairs = []
    n = len(file_paths)
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((file_paths[i], file_paths[j]))
    return pairs


# =============================================================================
# CLONE ANALYZER
# =============================================================================

class CloneAnalyzer:

    def __init__(self, config: AnalyzerConfig = None):
        self.config = config or AnalyzerConfig()
        self._init_detectors()
        print(f"\n{'='*60}")
        print("✅ CodeSpectra Clone Analyzer v3.1")
        print(f"{'='*60}")
        print(f"   Structural threshold : {self.config.structural_threshold}")
        print(f"   Semantic threshold   : {self.config.semantic_threshold}")
        print(f"   Type-4 pre-filter    : T1/T2/T3 < 0.50 required")
        print(f"   Cross-layer (IoT)    : {'enabled' if _CROSS_LAYER_AVAILABLE else 'unavailable'}")
        print(f"{'='*60}\n")

    def _init_detectors(self):
        from detectors.type1.type1_detector import Type1Detector
        from detectors.type2.type2_detector import Type2Detector
        from detectors.type3.hybrid_detector import Type3HybridDetector

        self._type1 = Type1Detector()
        self._type2 = Type2Detector()
        self._structural = Type3HybridDetector(
            hybrid_threshold=self.config.structural_threshold,
            ml_threshold=self.config.ml_threshold,
        )

        # Type-4: Educational Pipeline
        try:
            from detectors.type4.type4_detector import Type4Detector
            self._semantic = Type4Detector(threshold=self.config.semantic_threshold)
            print(f"✅ [Analyzer] Type-4 backend: {self._semantic.get_mode()}")
        except Exception as exc:
            print(f"⚠️  [Analyzer] Type-4 init failed ({exc}) — semantic detection disabled")
            self._semantic = None

    # =========================================================================
    # CROSS-LAYER CONTEXT — scanned once per batch, reused for every pair
    # =========================================================================

    def _get_layer_context(self, file_paths: List[str]) -> "LayerContext":
        """
        Run the IoT layer scan across all files in the batch.
        If the codebase looks like a regular student assignment,
        this returns immediately with is_multi_layer=False and costs almost nothing.
        """
        if not _CROSS_LAYER_AVAILABLE:
            # Module not installed — return a no-op context
            from dataclasses import dataclass

            @dataclass
            class _NoopContext:
                is_multi_layer = False
            return _NoopContext()

        return scan_batch_for_layers(file_paths)

    # =========================================================================
    # SMART BATCHING METHODS
    # =========================================================================

    def analyze_with_smart_batching(self, file_paths: List[str], detailed: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        n = len(file_paths)

        try:
            if psutil:
                available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)
                if available_memory < 2:
                    batch_size = 20
                elif available_memory < 4:
                    batch_size = 30
                else:
                    batch_size = 50
            else:
                batch_size = 30
        except:
            batch_size = 30

        num_batches = math.ceil(n / batch_size)
        total_pairs = n * (n - 1) // 2
        print(f"📊 Smart batching: {n} files → {num_batches} batches of ~{batch_size} files")
        print(f"📊 Total pairs to process: {total_pairs}")

        if n <= batch_size:
            return self._analyze_original(file_paths, detailed)

        all_pairs_results = []
        all_clone_classes = []
        all_fragment_pairs = []

        for batch_idx in range(num_batches):
            batch_start = batch_idx * batch_size
            batch_end = min(batch_start + batch_size, n)
            batch_files = file_paths[batch_start:batch_end]

            print(f"🔄 Processing batch {batch_idx + 1}/{num_batches}: {len(batch_files)} files")

            batch_result = self._analyze_batch(batch_files, detailed)

            if 'all_pairs' in batch_result:
                all_pairs_results.extend(batch_result.get('all_pairs', []))
            if 'clone_classes' in batch_result:
                all_clone_classes.extend(batch_result.get('clone_classes', []))
            if 'all_fragment_pairs' in batch_result:
                all_fragment_pairs.extend(batch_result.get('all_fragment_pairs', []))

            gc.collect()
            print(f"✅ Batch {batch_idx + 1} complete. Found {len(batch_result.get('all_pairs', []))} clone pairs")

        processing_time = (time.time() - start_time) * 1000

        return {
            "metadata": {
                "total_files": n,
                "total_comparisons": total_pairs,
                "processing_time_ms": round(processing_time, 2),
                "analysis_mode": "batched",
                "batches_processed": num_batches,
            },
            "class_analysis": {
                "is_simple_problem": False,
                "high_similarity_ratio": 0,
                "average_structural_similarity": 0,
                "message": f"Processed {n} files in {num_batches} batches",
                "outlier_pairs": [],
            },
            "statistics": {
                "structural": {"high": 0, "medium": 0, "low": 0, "similar_count": len(all_pairs_results)},
                "clone_types": {"type1": 0, "type2": 0, "type3": len(all_pairs_results), "type4": 0, "none": 0},
                "overall": {"high_similarity": 0, "medium_similarity": len(all_pairs_results), "needs_review": 0},
            },
            "pairs_needing_review": [],
            "all_pairs": all_pairs_results,
            "clone_classes": all_clone_classes,
        }

    def _analyze_batch(self, file_paths: List[str], detailed: bool) -> Dict:
        n = len(file_paths)
        if n < 2:
            return {"all_pairs": [], "clone_classes": [], "file_pair_scores": {}}

        # Scan the batch once for cross-layer signals — cheap, O(n) file reads
        layer_context = self._get_layer_context(file_paths)
        if layer_context.is_multi_layer:
            print(f"🌐 [Cross-Layer] {layer_context.reason}")

        self._structural.prepare_batch([Path(p) for p in file_paths])

        all_fragment_pairs = []
        file_pair_scores = {}
        pair_results = []

        for i in range(n):
            for j in range(i + 1, n):
                try:
                    result = self._analyze_pair(
                        file_paths[i], file_paths[j],
                        include_details=detailed,
                        layer_context=layer_context,
                    )
                    pair_results.append(result)

                    if hasattr(result.structural, 'all_type3_pairs') and result.structural.all_type3_pairs:
                        for fp in result.structural.all_type3_pairs:
                            all_fragment_pairs.append({
                                "frag_a": fp.get("frag_a"),
                                "frag_b": fp.get("frag_b"),
                                "similarity": fp.get("similarity", 0),
                            })

                    file_pair_scores[(i, j)] = max(result.structural.score, result.semantic.score)

                except Exception as e:
                    print(f"⚠️ Error analyzing pair ({i},{j}): {e}")
                    continue

        clone_classes = []
        if all_fragment_pairs:
            try:
                clone_classes = self._structural.clusterer.cluster(
                    all_fragment_pairs, min_similarity=self.config.structural_threshold
                )
            except Exception as e:
                print(f"⚠️ Error clustering: {e}")

        all_pairs = [self._pair_to_dict(p, detailed) for p in pair_results]

        return {
            "all_pairs": all_pairs,
            "clone_classes": clone_classes,
            "file_pair_scores": file_pair_scores,
            "all_fragment_pairs": all_fragment_pairs
        }

    def _analyze_original(self, file_paths: List[str], detailed: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        n = len(file_paths)
        same_lang_pairs = build_same_language_pairs(file_paths)
        total_comparisons = len(same_lang_pairs)

        print(f"📊 Analyzing {n} files ({total_comparisons} same-language pairs)…")

        # One-time batch scan — determines whether cross-layer logic fires at all
        layer_context = self._get_layer_context(file_paths)
        if layer_context.is_multi_layer:
            print(f"🌐 [Cross-Layer] {layer_context.reason}")

        self._structural.prepare_batch([Path(p) for p in file_paths])

        pairs: List[PairResult] = []
        for file_a, file_b in same_lang_pairs:
            pair = self._analyze_pair(file_a, file_b, include_details=detailed, layer_context=layer_context)
            pairs.append(pair)

        # For cross-layer codebases, also analyze cross-language pairs
        # (e.g. the JS watch file paired with the REST spec file —
        #  these would be skipped by build_same_language_pairs)
        if layer_context.is_multi_layer and _CROSS_LAYER_AVAILABLE:
            all_pair_keys = {(a, b) for a, b in same_lang_pairs}
            for file_a, file_b in _build_all_pairs(file_paths):
                if (file_a, file_b) not in all_pair_keys:
                    cl_result = analyze_cross_layer_pair(file_a, file_b, layer_context)
                    if cl_result and cl_result.matches:
                        # Emit a minimal PairResult so the frontend sees the cross-layer hit
                        stub = self._make_cross_layer_stub(file_a, file_b, cl_result)
                        pairs.append(stub)

        class_analysis = self._analyze_class(pairs)
        stats = self._calculate_stats(pairs)
        review_pairs = self._get_review_pairs(pairs, class_analysis)

        pairs.sort(key=lambda x: x.structural.score, reverse=True)

        processing_time = (time.time() - start_time) * 1000
        return self._build_response(
            pairs=pairs,
            class_analysis=class_analysis,
            stats=stats,
            review_pairs=review_pairs,
            total_files=n,
            total_comparisons=total_comparisons,
            processing_time=processing_time,
            detailed=detailed,
        )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(self, file_paths: List[str], detailed: bool = False) -> Dict[str, Any]:
        n = len(file_paths)
        total_pairs = n * (n - 1) // 2

        if n > 50 or total_pairs > 2000:
            print(f"⚠️ Large file set detected: {n} files, {total_pairs} pairs")
            print(f"🔄 Using smart batching to prevent overload")
            return self.analyze_with_smart_batching(file_paths, detailed)

        return self._analyze_original(file_paths, detailed)

    def analyze_for_assignment(self, student_submissions: List[Dict], language: str = "cpp",
                                extension_weights: Dict[str, float] = None, pair_timeout_seconds: int = 30,
                                skip_pairs: set = None, enable_type1: bool = True,
                                enable_type2: bool = True, enable_type3: bool = True,
                                enable_type4: bool = True) -> Dict[str, Any]:
        skip_pairs = skip_pairs or set()
        n = len(student_submissions)
        all_files = []
        for sub in student_submissions:
            all_files.extend(sub.get("files", []))

        # Scan the full file set once — for assignments this will almost always
        # return is_multi_layer=False and cost essentially nothing
        layer_context = self._get_layer_context(all_files)
        if layer_context.is_multi_layer:
            print(f"🌐 [Assignment Cross-Layer] {layer_context.reason}")

        self._structural.prepare_batch([Path(p) for p in all_files])
        clone_pairs = []
        remaining_pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) in skip_pairs:
                    continue
                sub_a = student_submissions[i]
                sub_b = student_submissions[j]
                try:
                    for fa in sub_a.get("files", []):
                        for fb in sub_b.get("files", []):
                            if not Path(fa).exists() or not Path(fb).exists():
                                continue
                            if _get_lang(fa) != _get_lang(fb):
                                continue
                            pair = self._analyze_pair(
                                fa, fb,
                                include_details=False,
                                enable_type1=enable_type1, enable_type2=enable_type2,
                                enable_type3=enable_type3, enable_type4=enable_type4,
                                layer_context=layer_context,
                            )
                            t1, t2, t3, t4 = pair.type1_score, pair.type2_score, pair.structural.score, pair.semantic.score
                            effective_score = max(t1, t2, t3, t4)
                            if effective_score < 0.25:
                                continue
                            pair_dict = {
                                "student_a_id": sub_a.get("student_id"), "student_b_id": sub_b.get("student_id"),
                                "submission_a_id": sub_a.get("submission_id"), "submission_b_id": sub_b.get("submission_id"),
                                "file_a": pair.file_a, "file_b": pair.file_b,
                                "type1_score": t1, "type2_score": t2, "structural_score": t3, "semantic_score": t4,
                                "effective_score": round(effective_score, 4),
                                "primary_clone_type": pair.primary_clone_type, "similarity_level": pair.similarity_level,
                                "needs_review": pair.needs_review, "summary": pair.summary,
                            }
                            # Attach cross-layer info if found (rare for assignments, but possible)
                            if pair.cross_layer:
                                pair_dict["cross_layer"] = pair.cross_layer.to_dict()
                            clone_pairs.append(pair_dict)
                except Exception as e:
                    print(f"⚠️ Pair ({i},{j}) error: {e}")
                    remaining_pairs.append([i, j])
        return {"clone_pairs": clone_pairs, "remaining_pairs": remaining_pairs, "class_analysis": {}}

    def get_pair_details(self, file_path_a: str, file_path_b: str) -> Dict[str, Any]:
        self._structural.prepare_batch([Path(file_path_a), Path(file_path_b)])
        # Scan the two-file context — might be a direct repo comparison
        layer_context = self._get_layer_context([file_path_a, file_path_b])
        pair = self._analyze_pair(file_path_a, file_path_b, include_details=True, layer_context=layer_context)
        return self._pair_to_dict(pair, detailed=True)

    # =========================================================================
    # PAIR ANALYSIS
    # =========================================================================

    def _analyze_pair(
        self,
        file_a: str,
        file_b: str,
        include_details: bool = False,
        enable_type1=True,
        enable_type2=True,
        enable_type3=True,
        enable_type4=True,
        layer_context=None,         # v3.1 — pass in pre-scanned context
    ) -> PairResult:
        path_a = Path(file_a)
        path_b = Path(file_b)
        t1_score = t2_score = 0.0
        if enable_type1:
            t1_score = self._type1.detect(file_a, file_b).get("type1_score", 0.0)
        if enable_type2:
            t2_score = self._type2.detect(file_a, file_b).get("type2_score", 0.0)
        structural = (
            self._run_structural(path_a, path_b, include_details)
            if enable_type3
            else StructuralResult(score=0.0, is_similar=False, confidence="UNLIKELY")
        )
        semantic = (
            self._run_semantic(path_a, path_b, t1_score, t2_score, structural.score, include_details)
            if enable_type4
            else SemanticResult(score=0.0, is_similar=False, confidence="UNLIKELY")
        )

        # v3.1 — run cross-layer analysis if the batch context says it's relevant.
        # This is a no-op (returns None) for all regular student assignment pairs.
        cross_layer_result = None
        if layer_context and _CROSS_LAYER_AVAILABLE:
            try:
                cross_layer_result = analyze_cross_layer_pair(file_a, file_b, layer_context)
            except Exception as e:
                print(f"⚠️ [Cross-Layer] Pair analysis failed for ({path_a.name}, {path_b.name}): {e}")

        primary_clone_type = self._determine_primary_clone_type(t1_score, t2_score, structural.score, semantic.score)
        level = self._get_similarity_level(structural, semantic)
        needs_review = self._should_review(structural, semantic)
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
            cross_layer=cross_layer_result,      # None when not applicable
        )

    def _make_cross_layer_stub(self, file_a: str, file_b: str, cl_result) -> PairResult:
        """
        Creates a minimal PairResult for a cross-layer pair that had no
        regular clone matches (e.g. JS watch file vs REST spec file).
        The cross_layer field carries the real payload here.
        """
        empty_structural = StructuralResult(score=0.0, is_similar=False, confidence="UNLIKELY")
        empty_semantic   = SemanticResult(score=0.0,   is_similar=False, confidence="UNLIKELY")
        return PairResult(
            file_a=Path(file_a).name,
            file_b=Path(file_b).name,
            structural=empty_structural,
            semantic=empty_semantic,
            similarity_level="CROSS_LAYER",
            needs_review=cl_result.cross_layer_score >= 0.3,
            summary=cl_result.explanation,
            primary_clone_type="cross_layer",
            cross_layer=cl_result,
        )

    def _determine_primary_clone_type(self, t1: float, t2: float, t3: float, t4: float) -> str:
        if t1 >= 0.98: return "type1"
        if t2 >= 0.90: return "type2"
        if t3 >= 0.50: return "type3"
        if t4 >= 0.60: return "type4"
        return "none"

    def _run_structural(self, file_a: Path, file_b: Path, include_details: bool) -> StructuralResult:
        raw = self._structural.detect(file_a, file_b)
        hybrid = raw["hybrid"]
        ml = raw.get("ml")
        hybrid_score = hybrid["score"]
        ml_score = ml["score"] if ml else None
        discrimination = raw.get("clone_type_discrimination", {})
        t3_found = discrimination.get("type3_pairs_detected", 0)
        t1_found = discrimination.get("type1_pairs_filtered", 0)
        t2_found = discrimination.get("type2_pairs_filtered", 0)
        if t3_found == 0 and (t1_found + t2_found) > 0:
            hybrid_score *= 0.40
        score = (hybrid_score * 0.6) + (ml_score * 0.4) if ml_score is not None else hybrid_score
        is_similar = hybrid_score >= self.config.structural_threshold
        if ml_score is not None and ml_score < 0.30 and hybrid_score < self.config.structural_high:
            is_similar = False
        confidence = self._get_confidence(score, "structural")
        details = None
        if include_details:
            detail_data = hybrid.get("details", {})
            details = StructuralDetails(
                winnowing_score=round(detail_data.get("winnowing_fingerprint_score", 0.0), 4),
                ast_score=round(detail_data.get("ast_skeleton_score", 0.0), 4),
                metrics_score=round(detail_data.get("complexity_metric_score", 0.0), 4),
                ml_score=round(ml_score, 4) if ml_score is not None else None,
                hybrid_score=round(hybrid_score, 4),
            )
        all_type3_pairs = raw.get("all_type3_pairs", [])
        return StructuralResult(score=round(score, 4), is_similar=is_similar, confidence=confidence,
                                details=details, discrimination=discrimination, all_type3_pairs=all_type3_pairs)

    def _run_semantic(self, file_a: Path, file_b: Path, t1: float, t2: float, t3: float,
                      include_details: bool = False) -> SemanticResult:
        if max(t1, t2, t3) >= 0.50 or self._semantic is None:
            return SemanticResult(score=0.0, is_similar=False, confidence="UNLIKELY", details=None)
        try:
            raw = self._semantic.detect(file_a, file_b, include_features=include_details)
            score = float(raw.get("semantic_score", 0.0))
            is_similar = bool(raw.get("is_semantic_clone", False))
            conf_raw = raw.get("confidence", "UNLIKELY")
            conf_map = {"HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW", "UNLIKELY": "UNLIKELY",
                        "high": "HIGH", "medium": "MEDIUM", "low": "LOW"}
            confidence = conf_map.get(str(conf_raw), "LOW")
            cat = raw.get("category_scores", {})
            details = None
            if include_details:
                details = SemanticDetails(
                    control_flow_score=float(cat.get("control_flow", 0.0)), data_flow_score=float(cat.get("data_flow", 0.0)),
                    call_pattern_score=float(cat.get("call_pattern", 0.0)), structural_score=float(cat.get("structural", 0.0)),
                    behavioral_score=float(cat.get("behavioral", 0.0)), behavioral_hash_a=str(raw.get("interpretation", "")), behavioral_hash_b=""
                )
            return SemanticResult(score=round(score, 4), is_similar=is_similar, confidence=confidence, details=details,
                                  io_match_score=raw.get("io_match_score"), io_available=bool(raw.get("io_available", False)),
                                  interpretation=str(raw.get("interpretation", "")))
        except Exception as exc:
            print(f"[Analyzer] Type-4 detect() error: {exc}")
            return SemanticResult(score=0.0, is_similar=False, confidence="UNLIKELY", details=None)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_confidence(self, score: float, analysis_type: str) -> str:
        if analysis_type == "structural":
            if score >= self.config.structural_high + 0.15: return "CRITICAL"
            if score >= self.config.structural_high: return "HIGH"
            if score >= self.config.structural_threshold: return "MEDIUM"
            if score >= 0.35: return "LOW"
            return "UNLIKELY"
        else:
            if score >= self.config.semantic_high + 0.10: return "CRITICAL"
            if score >= self.config.semantic_high: return "HIGH"
            if score >= self.config.semantic_threshold: return "MEDIUM"
            if score >= 0.40: return "LOW"
            return "UNLIKELY"

    def _get_similarity_level(self, structural: StructuralResult, semantic: SemanticResult) -> str:
        s = max(structural.score, semantic.score)
        if s >= 0.85: return "CRITICAL"
        if s >= 0.70: return "HIGH"
        if s >= 0.50: return "MEDIUM"
        if s >= 0.35: return "LOW"
        return "NONE"

    def _should_review(self, structural: StructuralResult, semantic: SemanticResult) -> bool:
        return max(structural.score, semantic.score) >= self.config.review_threshold

    def _generate_summary(self, structural: StructuralResult, semantic: SemanticResult,
                          level: str, primary_clone_type: str = "none") -> str:
        labels = {"type1": "Type-1 (Exact Copy)", "type2": "Type-2 (Renamed Variables)",
                  "type3": "Type-3 (Structural Clone)", "type4": "Type-4 (Semantic/Algorithmic Clone)",
                  "cross_layer": "Cross-Layer Feature Match",
                  "none": "No significant clone detected"}
        lbl = labels.get(primary_clone_type, "Unknown")
        if primary_clone_type == "type4" and semantic.details:
            interp = getattr(semantic.details, "behavioral_hash_a", "")
            if interp:
                return f"⚠️ {lbl} — {interp}"
            return f"⚠️ {lbl} — Semantic score: {semantic.score:.0%}. Review needed."
        if level in ("CRITICAL", "HIGH"):
            return f"⚠️ {lbl} — Structural: {structural.score:.0%}. Needs review."
        if level == "MEDIUM":
            return f"📋 {lbl} — Structural: {structural.score:.0%}. Consider reviewing."
        if level == "LOW":
            return f"ℹ️ Low similarity — Structural: {structural.score:.0%}."
        return "✅ No significant similarity detected."

    # =========================================================================
    # CLASS-WIDE ANALYSIS
    # =========================================================================

    def _analyze_class(self, pairs: List[PairResult]) -> "ClassAnalysis":
        if not pairs:
            return ClassAnalysis(False, 0.0, 0.0, 0.0, "No pairs to analyze")

        avg_struct = sum(p.structural.score for p in pairs) / len(pairs)
        avg_sem    = sum(p.semantic.score   for p in pairs) / len(pairs)
        high_count = sum(1 for p in pairs
                         if p.structural.score >= self.config.class_high_similarity_threshold)
        high_ratio = high_count / len(pairs)
        is_simple  = high_ratio >= self.config.simple_problem_ratio

        outliers = [
            {"file_a": p.file_a, "file_b": p.file_b,
             "structural_score": p.structural.score,
             "primary_clone_type": p.primary_clone_type}
            for p in pairs
            if p.structural.score >= avg_struct + 0.20
        ]

        if is_simple:
            msg = (f"⚠️ Simple problem: {high_ratio:.0%} of pairs show high similarity. "
                   f"May be expected for this assignment type.")
        elif high_count > 0:
            msg = f"📋 {high_count} pair(s) show high similarity and need review."
        else:
            msg = "✅ No concerning patterns detected."

        return ClassAnalysis(
            is_simple_problem       = is_simple,
            high_similarity_ratio   = round(high_ratio, 4),
            average_structural      = round(avg_struct, 4),
            average_semantic        = round(avg_sem, 4),
            message                 = msg,
            outlier_pairs           = outliers,
        )

    def _calculate_stats(self, pairs: List[PairResult]) -> Dict:
        return {
            "structural": {
                "high":          sum(1 for p in pairs if p.structural.confidence in ("HIGH", "CRITICAL")),
                "medium":        sum(1 for p in pairs if p.structural.confidence == "MEDIUM"),
                "low":           sum(1 for p in pairs if p.structural.confidence == "LOW"),
                "similar_count": sum(1 for p in pairs if p.structural.is_similar),
            },
            "clone_types": {
                "type1":       sum(1 for p in pairs if p.primary_clone_type == "type1"),
                "type2":       sum(1 for p in pairs if p.primary_clone_type == "type2"),
                "type3":       sum(1 for p in pairs if p.primary_clone_type == "type3"),
                "type4":       sum(1 for p in pairs if p.primary_clone_type == "type4"),
                "cross_layer": sum(1 for p in pairs if p.primary_clone_type == "cross_layer"),
                "none":        sum(1 for p in pairs if p.primary_clone_type == "none"),
            },
            "overall": {
                "high_similarity":   sum(1 for p in pairs if p.similarity_level in ("HIGH", "CRITICAL")),
                "medium_similarity": sum(1 for p in pairs if p.similarity_level == "MEDIUM"),
                "needs_review":      sum(1 for p in pairs if p.needs_review),
                # v3.1 — how many cross-layer matches were found in this batch?
                "cross_layer_pairs": sum(
                    1 for p in pairs
                    if p.cross_layer and p.cross_layer.is_cross_layer and p.cross_layer.matches
                ),
            },
        }

    def _get_review_pairs(self, pairs: List[PairResult], class_analysis: "ClassAnalysis") -> List[Dict]:
        review = [
            {
                "file_a":                  p.file_a,
                "file_b":                  p.file_b,
                "type1_score":             p.type1_score,
                "type2_score":             p.type2_score,
                "structural_score":        p.structural.score,
                "structural_confidence":   p.structural.confidence,
                "primary_clone_type":      p.primary_clone_type,
                "similarity_level":        p.similarity_level,
                "is_outlier":              p.structural.score >= class_analysis.average_structural + 0.15,
                "summary":                 p.summary,
            }
            for p in pairs if p.needs_review
        ]
        review.sort(key=lambda x: x["structural_score"], reverse=True)
        return review

    # =========================================================================
    # RESPONSE BUILDING
    # =========================================================================

    def _build_response(
        self, pairs, class_analysis, stats, review_pairs,
        total_files, total_comparisons, processing_time, detailed
    ) -> Dict[str, Any]:
        return {
            "metadata": {
                "total_files":        total_files,
                "total_comparisons":  total_comparisons,
                "processing_time_ms": round(processing_time, 2),
                "analysis_mode":      "detailed" if detailed else "summary",
            },
            "class_analysis": {
                "is_simple_problem":               class_analysis.is_simple_problem,
                "high_similarity_ratio":           class_analysis.high_similarity_ratio,
                "average_structural_similarity":   class_analysis.average_structural,
                "message":                         class_analysis.message,
                "outlier_pairs":                   class_analysis.outlier_pairs,
            },
            "statistics":           stats,
            "pairs_needing_review": review_pairs,
            "all_pairs": [self._pair_to_dict(p, detailed) for p in pairs],
        }

    def _pair_to_dict(self, pair: PairResult, detailed: bool) -> Dict:
        result = {
            "file_a":             pair.file_a,
            "file_b":             pair.file_b,
            "type1_score":        pair.type1_score,
            "type2_score":        pair.type2_score,
            "structural_score":   pair.structural.score,
            "semantic_score":     pair.semantic.score,
            "combined_score":     round(max(pair.structural.score, pair.semantic.score), 4),
            "primary_clone_type": pair.primary_clone_type,
            "similarity_level":   pair.similarity_level,
            "needs_review":       pair.needs_review,
            "summary":            pair.summary,
            "structural": {
                "score":      pair.structural.score,
                "confidence": pair.structural.confidence,
                "is_similar": pair.structural.is_similar,
            },
            "semantic": {
                "score":      pair.semantic.score,
                "confidence": pair.semantic.confidence,
                "is_similar": pair.semantic.is_similar,
            },
            "io_match_score":  pair.semantic.io_match_score,
            "io_available":    pair.semantic.io_available,
            "interpretation":  pair.semantic.interpretation,

            # v3.1 — cross-layer result attached here.
            # None → serialized as null in JSON, frontend can safely ignore it.
            "cross_layer": pair.cross_layer.to_dict() if pair.cross_layer else None,
        }

        if pair.structural.discrimination:
            result["clone_type_discrimination"] = pair.structural.discrimination

        if detailed and pair.structural.details:
            result["structural"]["details"] = {
                "winnowing_score": pair.structural.details.winnowing_score,
                "ast_score":       pair.structural.details.ast_score,
                "metrics_score":   pair.structural.details.metrics_score,
                "ml_score":        pair.structural.details.ml_score,
                "hybrid_score":    pair.structural.details.hybrid_score,
            }

        if detailed:
            result["fragments"] = self._serialize_fragments(
                pair.structural.all_type3_pairs or [],
                pair.primary_clone_type,
            )

        return result

    @staticmethod
    def _serialize_fragments(all_type3_pairs: List, clone_type: str) -> List[Dict]:
        """
        Convert Fragment dataclass objects into JSON-serializable dicts
        that include the actual source lines for side-by-side diff display.
        File paths are reduced to basenames only — no internal paths leak to the frontend.
        """
        out = []
        for p in all_type3_pairs:
            fa = p.get("frag_a")
            fb = p.get("frag_b")
            if fa is None or fb is None:
                continue

            def _frag_dict(frag) -> Dict:
                if isinstance(frag, dict):
                    return frag
                return {
                    "file":       frag.file_path,
                    "name":       frag.name,
                    "start_line": frag.start_line,
                    "end_line":   frag.end_line,
                    "source":     "\n".join(frag.source_lines) if hasattr(frag, "source_lines") else "",
                }

            fa_d = _frag_dict(fa)
            fb_d = _frag_dict(fb)

            name_a = Path(fa_d.get("file", "") or "").name or fa_d.get("file", "")
            name_b = Path(fb_d.get("file", "") or "").name or fb_d.get("file", "")

            out.append({
                "file_a":          name_a,
                "file_b":          name_b,
                "func_a":          fa_d.get("name", ""),
                "func_b":          fb_d.get("name", ""),
                "start_a":         fa_d.get("start_line", 0),
                "end_a":           fa_d.get("end_line", 0),
                "start_b":         fb_d.get("start_line", 0),
                "end_b":           fb_d.get("end_line", 0),
                "source_a":        fa_d.get("source", ""),
                "source_b":        fb_d.get("source", ""),
                "similarity":      round(float(p.get("similarity",      0)), 4),
                "raw_similarity":  round(float(p.get("raw_similarity",  0)), 4),
                "norm_similarity": round(float(p.get("norm_similarity", 0)), 4),
                "deep_similarity": round(float(p.get("deep_similarity", 0)), 4),
                "gap_ratio":       round(float(p.get("gap_ratio",       0)), 4),
                "clone_band":      p.get("clone_band", ""),
                "confidence":      p.get("confidence", ""),
                "similar_lines":   [],
            })
        return out


# =============================================================================
# CLASS ANALYSIS DATA CLASS (kept at module level for cross-reference)
# =============================================================================

@dataclass
class ClassAnalysis:
    is_simple_problem: bool
    high_similarity_ratio: float
    average_structural: float
    average_semantic: float
    message: str
    outlier_pairs: List[Dict] = field(default_factory=list)
