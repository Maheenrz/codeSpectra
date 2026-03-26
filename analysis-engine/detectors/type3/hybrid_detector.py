# detectors/type3/hybrid_detector.py
"""
Type-3 Hybrid Clone Detector — v3.0 (Multi-Tier + Aggregate Coverage)
======================================================================

Improvements over v2.x:
  1. Multi-tier MT3 detection (50–70% normalized similarity)
     Catches moderately-similar Type-3 clones that v2 missed entirely.

  2. Multi-fragment aggregate coverage score
     Previously: only the BEST single fragment pair was reported.
     Now: ALL Type-3 fragment pairs are aggregated into a clone_coverage
     score = total matched tokens across all pairs / tokens in smaller file.
     This catches distributed cloning (student copies 3 small functions,
     each below the threshold, but collectively >50% of the file is copied).

  3. Structural normalization (Level 2) used for MT3 confirmation
     for/while/do → LOOP, if/else → COND, etc.
     Helps when a student changes loop type to disguise copying.

  4. clone_type_discrimination now includes MT3 band counts
     Separate counters for VST3, ST3, MT3 pairs found.

  5. All Type-3 pairs (not just best) exposed in output
     Enables the CSV report generator to write one row per fragment pair.

Detection pipeline:
  Stage 1 — Fragment extraction (function/method level)
  Stage 2 — Dual-similarity comparison per fragment pair
             raw LCS + blind-norm LCS + structural-norm LCS
  Stage 3 — Multi-tier classification (Type-1/2/3 ST/MT, none)
  Stage 4 — Aggregate coverage computation
  Stage 5 — File-level heuristics (winnowing, AST, metrics)
  Stage 6 — Hybrid score combination (weighted ensemble)
  Stage 7 — Optional ML (BigCloneBench-trained Random Forest)
  Stage 8 — Final combined score

Score weights:
  structural_fragment : 0.40  (fragment dual-similarity — primary signal)
  winnowing           : 0.25  (k-gram fingerprinting — copy-paste detection)
  ast_skeleton        : 0.20  (control-flow structure comparison)
  complexity_metrics  : 0.15  (expanded 8-feature metric similarity)
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np

_DETECTOR_DIR = Path(__file__).resolve().parent
_REPO_ROOT    = _DETECTOR_DIR.parents[2]
sys.path.insert(0, str(_REPO_ROOT / "analysis-engine"))

from core.tokenizer import CodeTokenizer
from core.ast_processor import ASTProcessor
from core.ast_ml_adapter import ASTMLAdapter
from utils.metrics_calculator import MetricsCalculator
from utils.frequency_filter import BatchFrequencyFilter

from detectors.type3.winnowing import WinnowingDetector, WINNOWING_K
from detectors.type3.config.extension_weights import get_pair_weight
from detectors.type3.config.thresholds import get_thresholds, get_confidence
from detectors.type3.fragment_extractor import FragmentExtractor, Fragment
from detectors.type3.fragment_comparator import (
    compare_fragments,
    FragmentComparisonResult,
    TYPE3_ST_THRESHOLD,
    TYPE3_MT_THRESHOLD,
)
from detectors.type3.normalizer import normalize_tokens
from detectors.type3.lcs_comparator import get_matching_blocks
from detectors.type3.clone_clusterer import CloneClusterer


class Type3HybridDetector:
    """
    Hybrid Type-3 clone detector v3.0.

    Detects VST3, ST3, and MT3 clones with multi-fragment aggregation.
    """

    _EXT_LANG: dict[str, str] = {
        ".java": "java",
        ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
        ".c": "c", ".h": "cpp", ".hpp": "cpp",
        ".py": "python",
        ".js": "javascript", ".ts": "javascript",
        ".jsx": "javascript", ".tsx": "javascript",
    }

    def __init__(
        self,
        hybrid_threshold: float = 0.50,
        ml_threshold:     float = 0.382,
    ):
        self.tokenizer    = CodeTokenizer()
        self.ast_proc     = ASTProcessor()
        self.metrics_calc = MetricsCalculator()
        self.winnowing    = WinnowingDetector(k=WINNOWING_K, window_size=4)
        self.freq_filter  = BatchFrequencyFilter(threshold=0.70)

        self._extractor = FragmentExtractor(min_lines=5, min_tokens=15)
        self._clusterer = CloneClusterer()
        self._frag_cache: Dict[str, List[Fragment]] = {}

        self._adapter    = ASTMLAdapter(
            cache_dir=str(_REPO_ROOT / "analysis-engine" / "feature_cache")
        )
        self._models_dir = _DETECTOR_DIR / "models"
        self.clf:          Any        = None
        self.feature_names: List[str] = []
        self.ml_enabled:   bool       = False

        self._default_hybrid_threshold   = hybrid_threshold
        self._default_ml_threshold       = ml_threshold
        self._default_combined_threshold = 0.44

        self._load_model()

    # ─────────────────────────────────────────────────────────────────────
    # Model loading
    # ─────────────────────────────────────────────────────────────────────

    def _load_model(self) -> None:
        unified_model = self._models_dir / "type3_unified_model.joblib"
        unified_names = self._models_dir / "type3_unified_model.names.json"
        if unified_model.exists() and unified_names.exists():
            print("✅ [Type3] Loading unified model (BigCloneBench)")
            self.clf           = joblib.load(unified_model)
            self.feature_names = json.loads(unified_names.read_text())
            self.ml_enabled    = True
            return
        legacy_model = self._models_dir / "type3_rf_features.joblib"
        legacy_names = self._models_dir / "type3_rf_features.names.json"
        if legacy_model.exists() and legacy_names.exists():
            print("⚠️  [Type3] Using legacy model")
            self.clf           = joblib.load(legacy_model)
            self.feature_names = json.loads(legacy_names.read_text())
            self.ml_enabled    = True
            return
        print("⚠️  [Type3] No ML model — heuristics only")

    # ─────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────

    def _detect_language(self, path: Path) -> str:
        return self._EXT_LANG.get(path.suffix.lower(), "cpp")

    def _get_fragments(self, file_path: str) -> List[Fragment]:
        if file_path not in self._frag_cache:
            self._frag_cache[file_path] = self._extractor.extract(file_path)
        return self._frag_cache[file_path]

    def prepare_batch(self, all_file_paths: List[Path]) -> None:
        all_tokens = [self.tokenizer.tokenize_file(str(p)) for p in all_file_paths]
        self.freq_filter.train_on_batch(all_tokens, k=WINNOWING_K)
        for p in all_file_paths:
            self._get_fragments(str(p))

    def clear_cache(self) -> None:
        self._frag_cache.clear()

    # ─────────────────────────────────────────────────────────────────────
    # Stage 2–4: Fragment-level analysis with aggregate coverage
    # ─────────────────────────────────────────────────────────────────────

    def _structural_fragment_score(
        self, file_a: str, file_b: str
    ) -> Dict[str, Any]:
        """
        Compare two files at fragment level using the multi-tier approach.

        NEW in v3.0:
          - Collects ALL Type-3 pairs (VST3 + ST3 + MT3)
          - Computes aggregate clone_coverage
            = total Type-3 matched token weight / tokens in smaller file
          - Reports per-band counts in discrimination dict
          - Exposes all_type3_pairs for CSV export

        Returns:
          {
            "type3_score":      float,  # max(best_single, coverage * 0.85)
            "best_fragment_sim":float,  # best single fragment similarity
            "clone_coverage_a": float,  # fraction of file A's tokens in clone pairs
            "clone_coverage_b": float,  # fraction of file B's tokens in clone pairs
            "is_clone":         bool,
            "all_type3_pairs":  list,   # all pairs, used for CSV report
            "discrimination":   dict,   # per-band counts
          }
        """
        frags_a = self._get_fragments(file_a)
        frags_b = self._get_fragments(file_b)

        empty = {
            "type3_score":       0.0,
            "best_fragment_sim": 0.0,
            "clone_coverage_a":  0.0,
            "clone_coverage_b":  0.0,
            "is_clone":          False,
            "all_type3_pairs":   [],
            "discrimination": {
                "type1_pairs": 0, "type2_pairs": 0,
                "vst3_pairs":  0, "st3_pairs":   0,
                "mt3_pairs":   0, "none_pairs":  0,
            },
        }

        if not frags_a or not frags_b:
            return empty

        best_score   = 0.0
        all_t3_pairs: List[Dict] = []
        counts = defaultdict(int)

        # Track matched token weight for coverage computation
        # matched_weight_a[frag_key] = best type3_score × token_count for that frag
        matched_a: Dict[str, float] = {}
        matched_b: Dict[str, float] = {}

        for fa in frags_a:
            for fb in frags_b:
                result = compare_fragments(fa, fb)

                # Discrimination counts
                if result.clone_type == "type1":
                    counts["type1_pairs"] += 1
                elif result.clone_type == "type2":
                    counts["type2_pairs"] += 1
                elif result.clone_type == "type3":
                    band_key = f"{result.clone_band.lower()}_pairs"
                    counts[band_key] += 1
                else:
                    counts["none_pairs"] += 1

                if result.is_type3:
                    t3_pair = {
                        "frag_a":          fa,
                        "frag_b":          fb,
                        "similarity":      result.type3_score,
                        "raw_similarity":  result.raw_similarity,
                        "norm_similarity": result.norm_similarity,
                        "deep_similarity": result.deep_similarity,
                        "gap_ratio":       result.gap_ratio,
                        "clone_band":      result.clone_band,
                        "confidence":      result.confidence,
                    }
                    all_t3_pairs.append(t3_pair)

                    if result.type3_score > best_score:
                        best_score = result.type3_score

                    # Aggregate: track best match weight per fragment
                    # (a fragment can only be "claimed" once — use best match)
                    key_a = f"{fa.file_path}::{fa.name}::{fa.start_line}"
                    key_b = f"{fb.file_path}::{fb.name}::{fb.start_line}"
                    wa = result.type3_score * fa.token_count
                    wb = result.type3_score * fb.token_count
                    if wa > matched_a.get(key_a, 0):
                        matched_a[key_a] = wa
                    if wb > matched_b.get(key_b, 0):
                        matched_b[key_b] = wb

        # ── Aggregate clone coverage ─────────────────────────────────────
        # Fraction of each file's tokens that appear in clone pairs.
        # This is the key new metric: it catches distributed cloning where
        # many small fragments are copied but each is below the threshold alone.
        total_tokens_a = sum(f.token_count for f in frags_a)
        total_tokens_b = sum(f.token_count for f in frags_b)

        coverage_a = (sum(matched_a.values()) / max(total_tokens_a, 1))
        coverage_b = (sum(matched_b.values()) / max(total_tokens_b, 1))
        coverage_a = round(min(coverage_a, 1.0), 4)
        coverage_b = round(min(coverage_b, 1.0), 4)

        # ── Final type3_score ────────────────────────────────────────────
        # Take the max of:
        #   (a) best single fragment similarity  (individual pair quality)
        #   (b) average coverage × 0.85 penalty (aggregate clone extent)
        # The 0.85 penalty prevents coverage from overriding a genuine
        # high single-fragment match.
        avg_coverage   = (coverage_a + coverage_b) / 2.0
        coverage_score = round(avg_coverage * 0.85, 4)
        type3_score    = round(max(best_score, coverage_score), 4)

        return {
            "type3_score":       type3_score,
            "best_fragment_sim": round(best_score, 4),
            "clone_coverage_a":  coverage_a,
            "clone_coverage_b":  coverage_b,
            "is_clone":          type3_score >= TYPE3_ST_THRESHOLD,
            "all_type3_pairs":   all_t3_pairs,
            "discrimination": {
                "type1_pairs": counts["type1_pairs"],
                "type2_pairs": counts["type2_pairs"],
                "vst3_pairs":  counts["vst3_pairs"],
                "st3_pairs":   counts["st3_pairs"],
                "mt3_pairs":   counts["mt3_pairs"],
                "none_pairs":  counts["none_pairs"],
                # Legacy keys kept for backward compatibility
                "type3_pairs_detected": counts["vst3_pairs"] + counts["st3_pairs"] + counts["mt3_pairs"],
                "type1_pairs_filtered": counts["type1_pairs"],
                "type2_pairs_filtered": counts["type2_pairs"],
            },
        }

    # ─────────────────────────────────────────────────────────────────────
    # Stage 5: File-level heuristic scores
    # ─────────────────────────────────────────────────────────────────────

    def _hybrid_scores(self, file_a: Path, file_b: Path) -> Dict[str, Any]:
        tokens_a = self.tokenizer.tokenize_file(str(file_a))
        tokens_b = self.tokenizer.tokenize_file(str(file_b))

        if not tokens_a or not tokens_b:
            return {
                "winnowing": 0.0, "ast": 0.0, "metrics": 0.0,
                "structural": 0.0, "structural_result": {},
            }

        # Winnowing with boilerplate filter
        fp_a = self.winnowing.get_fingerprint(tokens_a)
        fp_b = self.winnowing.get_fingerprint(tokens_b)
        fp_a = {h for h in fp_a if h not in self.freq_filter.common_hashes}
        fp_b = {h for h in fp_b if h not in self.freq_filter.common_hashes}
        w_score = float(self.winnowing.calculate_similarity(fp_a, fp_b))

        # AST skeleton (keyword sequence)
        a_score = float(self.ast_proc.calculate_similarity(str(file_a), str(file_b)))

        # Expanded complexity metrics
        ma = self.metrics_calc.calculate_file_metrics(str(file_a))
        mb = self.metrics_calc.calculate_file_metrics(str(file_b))
        m_score = float(self.metrics_calc.calculate_similarity(ma, mb))

        # Fragment-level structural analysis (multi-tier)
        structural_result = self._structural_fragment_score(str(file_a), str(file_b))

        return {
            "winnowing":         w_score,
            "ast":               a_score,
            "metrics":           m_score,
            "structural":        structural_result["type3_score"],
            "structural_result": structural_result,
        }

    # ─────────────────────────────────────────────────────────────────────
    # Stage 7: ML score
    # ─────────────────────────────────────────────────────────────────────

    def _select_primary_unit(self, units):
        if not units:
            return None
        preferred = {"maxSubArray", "solve", "solution", "main", "Solution"}
        named = [u for u in units if getattr(u, "func_name", "") in preferred]
        pool = named if named else units
        pool.sort(key=lambda x: (x.features or {}).get("token_count", 0), reverse=True)
        return pool[0]

    def _ml_score(self, file_a: Path, file_b: Path) -> Optional[float]:
        if not self.ml_enabled or self.clf is None:
            return None
        try:
            units_a = self._adapter.build_units_from_file(str(file_a))
            units_b = self._adapter.build_units_from_file(str(file_b))
            if not units_a or not units_b:
                return None
            ua = self._select_primary_unit(units_a)
            ub = self._select_primary_unit(units_b)
            if ua is None or ub is None:
                return None
            for u in (ua, ub):
                self._adapter.normalize_unit(u)
                self._adapter.compute_subtree_hashes(u)
                self._adapter.extract_ast_paths(u)
                self._adapter.compute_ast_counts(u)
            self._adapter.vectorize_units([ua], method="tfidf")
            self._adapter.vectorize_units([ub], method="tfidf")
            feats = self._adapter.make_pair_features(ua, ub)
            fa_f  = ua.features or {}
            fb_f  = ub.features or {}
            feature_map = {
                "jaccard_subtrees":     feats.get("jaccard_subtrees",     0.0),
                "cosine_paths":         feats.get("cosine_paths",         0.0),
                "abs_token_count_diff": feats.get("abs_token_count_diff", 0.0),
                "avg_token_count":      feats.get("avg_token_count",      0.0),
                "subtree_count_A":      len(ua.subtree_hashes or set()),
                "subtree_count_B":      len(ub.subtree_hashes or set()),
                "path_count_A":         len(ua.ast_paths or []),
                "path_count_B":         len(ub.ast_paths or []),
                "token_count_A":        fa_f.get("token_count", 0),
                "token_count_B":        fb_f.get("token_count", 0),
                "call_approx_A":        fa_f.get("call_approx", 0),
                "call_approx_B":        fb_f.get("call_approx", 0),
            }
            vec = np.array(
                [float(feature_map.get(n, 0.0)) for n in self.feature_names],
                dtype=np.float32,
            ).reshape(1, -1)
            if hasattr(self.clf, "predict_proba"):
                return float(self.clf.predict_proba(vec)[0][1])
            return float(self.clf.predict(vec)[0])
        except Exception as e:
            print(f"⚠️  [Type3] ML error: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────
    # Diff blocks for frontend highlighting
    # ─────────────────────────────────────────────────────────────────────

    def get_diff_blocks(self, file_a: str, file_b: str) -> List[Dict]:
        sr = self._structural_fragment_score(file_a, file_b)
        if not sr["all_type3_pairs"]:
            return []
        best = max(sr["all_type3_pairs"], key=lambda p: p["similarity"])
        fa   = best["frag_a"]
        fb   = best["frag_b"]
        norm_a = normalize_tokens(fa.tokens)
        norm_b = normalize_tokens(fb.tokens)
        blocks = get_matching_blocks(norm_a, norm_b)
        return [{"i": i, "j": j, "n": n} for i, j, n in blocks if n > 0]

    # ─────────────────────────────────────────────────────────────────────
    # Public API — single pair detection
    # ─────────────────────────────────────────────────────────────────────

    def detect(
        self,
        file_path_a: "str | Path",
        file_path_b: "str | Path",
    ) -> Dict[str, Any]:
        """
        Compare two files and return a structured detection result.

        New in v3.0:
          - "all_type3_pairs" in output for CSV export
          - "clone_coverage_a/b" showing how much of each file is cloned
          - "best_fragment_sim" for the highest single-fragment similarity
          - Per-band discrimination counts (vst3, st3, mt3)
        """
        fa = Path(file_path_a)
        fb = Path(file_path_b)

        language   = self._detect_language(fa)
        thresholds = get_thresholds(language)
        ext_weight = get_pair_weight(str(fa), str(fb))

        h  = self._hybrid_scores(fa, fb)
        sr = h["structural_result"]

        # Weighted combination (Stage 6)
        raw_hybrid = (
            h["structural"] * 0.40
            + h["winnowing"] * 0.25
            + h["ast"]       * 0.20
            + h["metrics"]   * 0.15
        )
        hybrid_score = raw_hybrid * ext_weight

        # Hybrid discount when ONLY type1/2 fragments (no genuine type3)
        disc         = sr.get("discrimination", {})
        t3_found     = disc.get("type3_pairs_detected", 0)
        any_type12   = (disc.get("type1_pairs", 0) + disc.get("type2_pairs", 0)) > 0
        if t3_found == 0 and any_type12:
            hybrid_score = hybrid_score * 0.40

        hybrid = {
            "score":    round(hybrid_score, 4),
            "is_clone": bool(hybrid_score >= thresholds["hybrid"]),
            "details": {
                "structural_fragment_score":   round(h["structural"], 4),
                "winnowing_fingerprint_score": round(h["winnowing"],  4),
                "ast_skeleton_score":          round(h["ast"],        4),
                "complexity_metric_score":     round(h["metrics"],    4),
                "extension_weight":            round(ext_weight,       4),
                "best_fragment_sim":           sr.get("best_fragment_sim", 0.0),
                "clone_coverage_a":            sr.get("clone_coverage_a",  0.0),
                "clone_coverage_b":            sr.get("clone_coverage_b",  0.0),
            },
        }

        # ML score (Stage 7)
        raw_ml = self._ml_score(fa, fb)
        if raw_ml is not None:
            ml_score = raw_ml * ext_weight
            ml = {
                "score":    round(ml_score, 4),
                "is_clone": bool(ml_score >= thresholds["ml"]),
                "threshold_used": thresholds["ml"],
            }
        else:
            ml_score = None
            ml       = None

        # Final combined score (Stage 8)
        if ml_score is not None:
            combined_score = hybrid_score * 0.50 + ml_score * 0.50
        else:
            combined_score = hybrid_score

        combined_is_clone = bool(combined_score >= thresholds["combined"])
        confidence        = get_confidence(combined_score)
        combined = {
            "score":      round(combined_score, 4),
            "is_clone":   combined_is_clone,
            "confidence": confidence,
        }

        return {
            "hybrid":              hybrid,
            "ml":                  ml,
            "combined":            combined,
            "is_clone":            combined_is_clone,
            "language":            language,
            "extension_weight":    round(ext_weight, 4),
            "thresholds":          thresholds,
            # Discrimination and coverage data
            "clone_type_discrimination": {
                "type1_pairs_filtered": disc.get("type1_pairs", 0),
                "type2_pairs_filtered": disc.get("type2_pairs", 0),
                "type3_pairs_detected": t3_found,
                "vst3_pairs":           disc.get("vst3_pairs", 0),
                "st3_pairs":            disc.get("st3_pairs",  0),
                "mt3_pairs":            disc.get("mt3_pairs",  0),
                "none_pairs":           disc.get("none_pairs", 0),
                "best_fragment_sim":    sr.get("best_fragment_sim", 0.0),
                "clone_coverage_a":     sr.get("clone_coverage_a",  0.0),
                "clone_coverage_b":     sr.get("clone_coverage_b",  0.0),
            },
            # All type3 pairs for CSV export
            "all_type3_pairs": sr.get("all_type3_pairs", []),
        }

    # ─────────────────────────────────────────────────────────────────────
    # Batch detection
    # ─────────────────────────────────────────────────────────────────────

    def detect_clones(self, all_file_paths: List[str]):
        results = []
        n = len(all_file_paths)
        self.prepare_batch([Path(p) for p in all_file_paths])
        for i in range(n):
            for j in range(i + 1, n):
                out  = self.detect(all_file_paths[i], all_file_paths[j])
                cs   = out["combined"]["score"]
                conf = out["combined"]["confidence"]
                if out["is_clone"] or conf in ("HIGH", "MEDIUM"):
                    results.append({
                        "file_a":         all_file_paths[i],
                        "file_b":         all_file_paths[j],
                        "is_clone":       out["is_clone"],
                        "hybrid_score":   out["hybrid"]["score"],
                        "ml_score":       out["ml"]["score"] if out["ml"] else None,
                        "combined_score": cs,
                        "confidence":     conf,
                        "language":       out["language"],
                        "extension_weight": out["extension_weight"],
                        "details":        out["hybrid"]["details"],
                        "all_type3_pairs": out.get("all_type3_pairs", []),
                    })
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        return DetectionResultWrapper(results)

    def get_clone_type(self) -> str:
        return "type3"


class DetectionResultWrapper:
    def __init__(self, matches: list):
        self.clone_groups     = matches
        self.total_clones     = sum(1 for m in matches if m.get("is_clone"))
        self.total_suspicious = len(matches)

    def get_high_confidence_clones(self) -> list:
        return [m for m in self.clone_groups if m.get("confidence") == "HIGH"]

    def get_clones_by_confidence(self, confidence: str) -> list:
        return [m for m in self.clone_groups if m.get("confidence") == confidence]
