# detectors/type3/hybrid_detector.py
"""
Type-3 Hybrid Clone Detector
=============================

Detection pipeline:
  1. Winnowing fingerprints  (k=7, Jaccard)   weight: 0.50
  2. AST skeleton similarity (SequenceMatcher) weight: 0.35
  3. Complexity metrics      (Euclidean)       weight: 0.15
  →  hybrid_score = weighted sum of the three

  4. ML model (Random Forest trained on BigCloneBench features)

  5. combined_score = hybrid * 0.50 + ml * 0.50
     (OR hybrid alone when ML unavailable)

  6. Final verdict = combined_score >= language threshold
     (previously AND logic — replaced with combined score for better recall)

  7. Extension weight applied as a multiplier:
     .h/.hpp files are near-identical boilerplate → scored at 0.35×
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np

# Ensure package root is on sys.path when run directly
_DETECTOR_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _DETECTOR_DIR.parents[2]
sys.path.insert(0, str(_REPO_ROOT / "analysis-engine"))

from core.tokenizer import CodeTokenizer
from core.ast_processor import ASTProcessor
from core.ast_ml_adapter import ASTMLAdapter
from utils.metrics_calculator import MetricsCalculator
from utils.frequency_filter import BatchFrequencyFilter

from detectors.type3.winnowing import WinnowingDetector, WINNOWING_K
from detectors.type3.config.extension_weights import get_pair_weight
from detectors.type3.config.thresholds import get_thresholds, get_confidence
from detectors.type3.nicad_detector import NiCadDetector


class Type3HybridDetector:
    """
    Hybrid Type-3 clone detector with:
    - Corrected hybrid weights  (winnowing 50%, AST 35%, metrics 15%)
    - Combined-score final verdict (no more fragile AND logic)
    - Extension-aware weighting  (.h files discounted)
    - Language-specific thresholds from config/thresholds.py
    """

    # Extension → language for threshold lookup
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
        ml_threshold: float = 0.382,
    ):
        # ── Heuristic components ──────────────────────────────────────────
        self.tokenizer   = CodeTokenizer()
        self.ast_proc    = ASTProcessor()
        self.metrics_calc = MetricsCalculator()
        self.winnowing   = WinnowingDetector(k=WINNOWING_K, window_size=4)
        # freq_filter k must match winnowing k so the same k-gram hashes are compared
        self.freq_filter = BatchFrequencyFilter(threshold=0.70)
        self.nicad = NiCadDetector(similarity_threshold=0.70, min_fragment_lines=6)
        # ── ML components ────────────────────────────────────────────────
        self._adapter    = ASTMLAdapter(
            cache_dir=str(_REPO_ROOT / "analysis-engine" / "feature_cache")
        )
        self._models_dir = _DETECTOR_DIR / "models"
        self.clf: Any    = None
        self.feature_names: List[str] = []
        self.ml_enabled: bool = False

        # Fallback thresholds (overridden per call via config)
        self._default_hybrid_threshold   = hybrid_threshold
        self._default_ml_threshold       = ml_threshold
        self._default_combined_threshold = 0.44

        self._load_model()

    # ─────────────────────────────────────────────────────────────────────
    # Model loading
    # ─────────────────────────────────────────────────────────────────────

    def _load_model(self) -> None:
        unified_model  = self._models_dir / "type3_unified_model.joblib"
        unified_names  = self._models_dir / "type3_unified_model.names.json"

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

        print("⚠️  [Type3] No ML model found — using heuristics only")

    # ─────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────

    def _detect_language(self, path: Path) -> str:
        return self._EXT_LANG.get(path.suffix.lower(), "cpp")

    def prepare_batch(self, all_file_paths: List[Path]) -> None:
        all_tokens = [self.tokenizer.tokenize_file(str(p)) for p in all_file_paths]
        self.freq_filter.train_on_batch(all_tokens, k=WINNOWING_K)
        self.nicad.prepare_batch([str(p) for p in all_file_paths])
        
    # ─────────────────────────────────────────────────────────────────────
    # Hybrid heuristic scores
    # ─────────────────────────────────────────────────────────────────────

    def _hybrid_scores(self, file_a: Path, file_b: Path) -> Dict[str, float]:
        tokens_a = self.tokenizer.tokenize_file(str(file_a))
        tokens_b = self.tokenizer.tokenize_file(str(file_b))

        if not tokens_a or not tokens_b:
            return {"winnowing": 0.0, "ast": 0.0, "metrics": 0.0, "nicad": 0.0}

        # Winnowing (boilerplate removed)
        fp_a = self.winnowing.get_fingerprint(tokens_a)
        fp_b = self.winnowing.get_fingerprint(tokens_b)
        fp_a = {h for h in fp_a if h not in self.freq_filter.common_hashes}
        fp_b = {h for h in fp_b if h not in self.freq_filter.common_hashes}
        w_score = float(self.winnowing.calculate_similarity(fp_a, fp_b))

        # AST skeleton (keyword sequence)
        a_score = float(self.ast_proc.calculate_similarity(str(file_a), str(file_b)))

        # Complexity metrics
        ma = self.metrics_calc.calculate_file_metrics(str(file_a))
        mb = self.metrics_calc.calculate_file_metrics(str(file_b))
        m_score = float(self.metrics_calc.calculate_similarity(ma, mb))

        # NiCad fragment-level LCS (NEW — dominant signal)
        nicad_result = self.nicad.detect(str(file_a), str(file_b))
        n_score = float(nicad_result["nicad_score"])

        return {"winnowing": w_score, "ast": a_score, "metrics": m_score, "nicad": n_score}

    # ─────────────────────────────────────────────────────────────────────
    # ML feature vector
    # ─────────────────────────────────────────────────────────────────────

    def _select_primary_unit(self, units):
        if not units:
            return None
        preferred = {"maxSubArray", "solve", "solution", "main", "Solution"}
        named = [u for u in units if getattr(u, "func_name", "") in preferred]
        pool = named if named else units
        pool.sort(
            key=lambda x: (x.features or {}).get("token_count", 0), reverse=True
        )
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
            fa = ua.features or {}
            fb = ub.features or {}

            feature_map = {
                "jaccard_subtrees":     feats.get("jaccard_subtrees", 0.0),
                "cosine_paths":         feats.get("cosine_paths", 0.0),
                "abs_token_count_diff": feats.get("abs_token_count_diff", 0.0),
                "avg_token_count":      feats.get("avg_token_count", 0.0),
                "subtree_count_A":      len(ua.subtree_hashes or set()),
                "subtree_count_B":      len(ub.subtree_hashes or set()),
                "path_count_A":         len(ua.ast_paths or []),
                "path_count_B":         len(ub.ast_paths or []),
                "token_count_A":        fa.get("token_count", 0),
                "token_count_B":        fb.get("token_count", 0),
                "call_approx_A":        fa.get("call_approx", 0),
                "call_approx_B":        fb.get("call_approx", 0),
            }

            vec = np.array(
                [float(feature_map.get(n, 0.0)) for n in self.feature_names],
                dtype=np.float32,
            ).reshape(1, -1)

            if hasattr(self.clf, "predict_proba"):
                return float(self.clf.predict_proba(vec)[0][1])
            return float(self.clf.predict(vec)[0])

        except Exception as e:
            print(f"⚠️  [Type3] ML extraction error: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────

    def detect(
        self,
        file_path_a: "str | Path",
        file_path_b: "str | Path",
    ) -> Dict[str, Any]:
        """
        Compare two files and return a structured detection result.

        Returns:
        {
            "hybrid":   {"score": float, "is_clone": bool, "details": {...}},
            "ml":       {"score": float, "is_clone": bool} | None,
            "combined": {"score": float, "is_clone": bool, "confidence": str},
            "is_clone": bool,          ← combined_score >= threshold
            "language": str,
            "extension_weight": float, ← pair weight (1.0 for .cpp, 0.35 for .h)
            "thresholds": {...},
        }
        """
        fa = Path(file_path_a)
        fb = Path(file_path_b)

        language   = self._detect_language(fa)
        thresholds = get_thresholds(language)
        ext_weight = get_pair_weight(str(fa), str(fb))

        # ── Hybrid heuristics ────────────────────────────────────────────
        h = self._hybrid_scores(fa, fb)

        # FIXED weights: winnowing 50%, AST 35%, metrics 15%, NiCad 70%
        raw_hybrid = (
            h["nicad"]    * 0.40   # fragment LCS — most reliable for Type-3
            + h["winnowing"] * 0.30   # k-gram fingerprinting
            + h["ast"]       * 0.20   # control-flow skeleton
            + h["metrics"]   * 0.10   # cyclomatic complexity
        )

        # Apply extension weight (headers etc. are discounted)
        hybrid_score = raw_hybrid * ext_weight

        hybrid = {
            "score":    round(hybrid_score, 4),
            "is_clone": bool(hybrid_score >= thresholds["hybrid"]),
            "details": {
                "nicad_fragment_score":         round(h["nicad"],     4),
                "winnowing_fingerprint_score":  round(h["winnowing"], 4),
                "ast_skeleton_score":           round(h["ast"],       4),
                "complexity_metric_score":      round(h["metrics"],   4),
                "extension_weight":             round(ext_weight,      4),
            },
        }

        # ── ML score ─────────────────────────────────────────────────────
        raw_ml = self._ml_score(fa, fb)
        if raw_ml is not None:
            ml_score = raw_ml * ext_weight   # also discount ML by ext weight
            ml = {
                "score":          round(ml_score, 4),
                "is_clone":       bool(ml_score >= thresholds["ml"]),
                "threshold_used": thresholds["ml"],
            }
        else:
            ml_score = None
            ml = None

        # ── Combined score ───────────────────────────────────────────────
        if ml_score is not None:
            combined_score = hybrid_score * 0.50 + ml_score * 0.50
        else:
            combined_score = hybrid_score   # ML unavailable → use hybrid alone

        combined_is_clone = bool(combined_score >= thresholds["combined"])
        confidence        = get_confidence(combined_score)

        combined = {
            "score":    round(combined_score, 4),
            "is_clone": combined_is_clone,
            "confidence": confidence,
        }

        return {
            "hybrid":           hybrid,
            "ml":               ml,
            "combined":         combined,
            "is_clone":         combined_is_clone,   # ← combined score, NOT AND logic
            "language":         language,
            "extension_weight": round(ext_weight, 4),
            "thresholds":       thresholds,
        }

    def detect_clones(self, all_file_paths: List[str]):
        """Batch detection — returns DetectionResultWrapper sorted by score."""
        results = []
        n = len(all_file_paths)
        self.prepare_batch([Path(p) for p in all_file_paths])

        for i in range(n):
            for j in range(i + 1, n):
                out = self.detect(all_file_paths[i], all_file_paths[j])
                combined_score = out["combined"]["score"]
                confidence     = out["combined"]["confidence"]

                if out["is_clone"] or confidence in ("HIGH", "MEDIUM"):
                    results.append({
                        "file_a":         all_file_paths[i],
                        "file_b":         all_file_paths[j],
                        "is_clone":       out["is_clone"],
                        "hybrid_score":   out["hybrid"]["score"],
                        "ml_score":       out["ml"]["score"] if out["ml"] else None,
                        "combined_score": combined_score,
                        "confidence":     confidence,
                        "language":       out["language"],
                        "extension_weight": out["extension_weight"],
                        "details":        out["hybrid"]["details"],
                    })

        results.sort(key=lambda x: x["combined_score"], reverse=True)
        return DetectionResultWrapper(results)

    def get_clone_type(self) -> str:
        return "type3"


class DetectionResultWrapper:
    def __init__(self, matches: list):
        self.clone_groups    = matches
        self.total_clones    = sum(1 for m in matches if m.get("is_clone"))
        self.total_suspicious = len(matches)

    def get_high_confidence_clones(self) -> list:
        return [m for m in self.clone_groups if m.get("confidence") == "HIGH"]

    def get_clones_by_confidence(self, confidence: str) -> list:
        return [m for m in self.clone_groups if m.get("confidence") == confidence]