from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import json
import joblib
import numpy as np

from core.tokenizer import CodeTokenizer
from utils.metrics_calculator import MetricsCalculator
from core.ast_processor import ASTProcessor
from detectors.type3.winnowing import WinnowingDetector
from utils.frequency_filter import BatchFrequencyFilter

# ML (named pair features via ASTMLAdapter)
# Ensure analysis-engine is importable
DETECTOR_DIR = Path(__file__).resolve().parent
REPO_ROOT = DETECTOR_DIR.parents[2]  # repo_root
sys.path.insert(0, str(REPO_ROOT / "analysis-engine"))
from core.ast_ml_adapter import ASTMLAdapter  # adjust if your adapter filename differs


class Type3HybridDetector:
    """
    Hybrid detector that returns:
      - Hybrid pipeline (Winnowing + AST + Metrics): score, is_clone, details
      - ML (RandomForest on named pair features): score, is_clone (if model available)
    """
    def __init__(self, hybrid_threshold: float = 0.45, ml_threshold: float = 0.50):
        # Heuristic components
        self.tokenizer = CodeTokenizer()
        self.metrics_calc = MetricsCalculator()
        self.ast_processor = ASTProcessor()
        self.winnowing = WinnowingDetector(k=5, window_size=4)
        self.freq_filter = BatchFrequencyFilter(threshold=0.7)

        # ML components
        self.hybrid_threshold = hybrid_threshold
        self.ml_threshold = ml_threshold
        self.adapter = ASTMLAdapter(cache_dir=str(REPO_ROOT / "analysis-engine" / "feature_cache"))
        self.models_dir = DETECTOR_DIR / "models"

        self.ml_enabled = False
        self.feature_names: List[str] = []
        self.clf = None

        # Preferred: named-feature model trained on pairs_features.csv
        features_model = self.models_dir / "type3_rf_features.joblib"
        features_names = self.models_dir / "type3_rf_features.names.json"

        if features_model.exists() and features_names.exists():
            self.clf = joblib.load(features_model)
            self.feature_names = json.loads(features_names.read_text())
            self.ml_enabled = True
        else:
            # If you only have TF-IDF model, serving raw code requires reproducing the same vectorizer; we skip here.
            self.ml_enabled = False

    def prepare_batch(self, all_file_paths: List[Path]):
        """
        Train the frequency filter on the whole batch to remove common boilerplate.
        Must be called BEFORE detect() for correct Winnowing behavior.
        """
        all_tokens = [self.tokenizer.tokenize_file(str(p)) for p in all_file_paths]
        self.freq_filter.train_on_batch(all_tokens)

    # ---------- Hybrid heuristic pipeline ----------
    def _hybrid_scores(self, file_a: Path, file_b: Path) -> Dict[str, float]:
        tokens_a = self.tokenizer.tokenize_file(str(file_a))
        tokens_b = self.tokenizer.tokenize_file(str(file_b))
        if not tokens_a or not tokens_b:
            return {"winnowing": 0.0, "ast": 0.0, "metrics": 0.0}

        # Winnowing fingerprints with boilerplate removal
        set_a = self.winnowing.get_fingerprint(tokens_a)
        set_b = self.winnowing.get_fingerprint(tokens_b)
        set_a = {h for h in set_a if h not in self.freq_filter.common_hashes}
        set_b = {h for h in set_b if h not in self.freq_filter.common_hashes}
        w_score = float(self.winnowing.calculate_similarity(set_a, set_b))

        # AST skeleton similarity (loops/ifs/etc.)
        a_score = float(self.ast_processor.calculate_similarity(str(file_a), str(file_b)))

        # Complexity shape similarity
        ma = self.metrics_calc.calculate_file_metrics(str(file_a))
        mb = self.metrics_calc.calculate_file_metrics(str(file_b))
        m_score = float(self.metrics_calc.calculate_similarity(ma, mb))

        return {"winnowing": w_score, "ast": a_score, "metrics": m_score}

    # ---------- ML pipeline (RandomForest on named pair features) ----------
    def _select_primary_unit(self, units: List) -> Optional[Any]:
        if not units:
            return None
        # Normalize and compute counts to help selection
        for u in units:
            try:
                self.adapter.normalize_unit(u)
                self.adapter.compute_ast_counts(u)  # fills u.features["token_count"]
            except Exception:
                pass
        preferred = {"maxSubArray", "solve", "solution", "main"}
        named = [u for u in units if getattr(u, "func_name", "") in preferred]
        if named:
            named.sort(key=lambda x: (x.features or {}).get("token_count", 0), reverse=True)
            return named[0]
        units.sort(key=lambda x: (x.features or {}).get("token_count", 0), reverse=True)
        return units[0]

    def _ml_vec(self, file_a: Path, file_b: Path) -> Optional[np.ndarray]:
        try:
            units_a = self.adapter.build_units_from_file(str(file_a))
            units_b = self.adapter.build_units_from_file(str(file_b))
            if not units_a or not units_b:
                return None
            ua = self._select_primary_unit(units_a)
            ub = self._select_primary_unit(units_b)
            if ua is None or ub is None:
                return None

            # Prepare named pair features
            self.adapter.normalize_unit(ua); self.adapter.normalize_unit(ub)
            self.adapter.compute_subtree_hashes(ua); self.adapter.compute_subtree_hashes(ub)
            self.adapter.extract_ast_paths(ua); self.adapter.extract_ast_paths(ub)
            self.adapter.compute_ast_counts(ua); self.adapter.compute_ast_counts(ub)
            # Optional per-unit TF-IDF for cosine_paths
            self.adapter.vectorize_units([ua], method="tfidf")
            self.adapter.vectorize_units([ub], method="tfidf")

            feats = self.adapter.make_pair_features(ua, ub)
            fa = ua.features or {}; fb = ub.features or {}
            feature_map = {
                "jaccard_subtrees": feats.get("jaccard_subtrees", 0.0),
                "cosine_paths": feats.get("cosine_paths", 0.0),
                "abs_token_count_diff": feats.get("abs_token_count_diff", 0.0),
                "avg_token_count": feats.get("avg_token_count", 0.0),
                "subtree_count_A": len(ua.subtree_hashes or []),
                "subtree_count_B": len(ub.subtree_hashes or []),
                "path_count_A": len(ua.ast_paths or []),
                "path_count_B": len(ub.ast_paths or []),
                "token_count_A": fa.get("token_count", 0),
                "token_count_B": fb.get("token_count", 0),
                "call_approx_A": fa.get("call_approx", 0),
                "call_approx_B": fb.get("call_approx", 0),
            }
            vec = np.array([float(feature_map.get(n, 0.0)) for n in self.feature_names], dtype=np.float32)
            return vec
        except Exception:
            return None

    # ---------- Unified detect ----------
    def detect(self, file_path_a: str | Path, file_path_b: str | Path) -> Dict[str, Any]:
        """
        Returns separate results:
          {
            "hybrid": { "score": float, "is_clone": bool, "details": {...} },
            "ml":     { "score": float, "is_clone": bool }  # present only if model loaded
          }
        """
        file_a = Path(file_path_a)
        file_b = Path(file_path_b)

        # Hybrid heuristics
        h = self._hybrid_scores(file_a, file_b)
        hybrid_score = (h["winnowing"] * 0.3) + (h["ast"] * 0.6) + (h["metrics"] * 0.1)
        hybrid = {
            "score": round(hybrid_score, 4),
            "is_clone": bool(hybrid_score >= self.hybrid_threshold),
            "details": {
                "winnowing_fingerprint_score": round(h["winnowing"], 4),
                "ast_skeleton_score": round(h["ast"], 4),
                "complexity_metric_score": round(h["metrics"], 4),
            },
        }

        # ML
        ml = None
        if self.ml_enabled and self.clf is not None:
            vec = self._ml_vec(file_a, file_b)
            if vec is not None and vec.size > 0:
                vec = vec.reshape(1, -1)
                if hasattr(self.clf, "predict_proba"):
                    score = float(self.clf.predict_proba(vec)[0][1])
                    ml = {"score": round(score, 4), "is_clone": bool(score >= self.ml_threshold)}
                else:
                    pred = int(self.clf.predict(vec)[0])
                    ml = {"score": float(pred), "is_clone": bool(pred == 1)}

        return {"hybrid": hybrid, "ml": ml}

    def detect_clones(self, all_file_paths: List[str]):
        """
        Retained for compatibility (returns only hybrid matches).
        Prefer using detect() per pair for detailed outputs.
        """
        results = []
        n = len(all_file_paths)
        self.prepare_batch([Path(p) for p in all_file_paths])

        for i in range(n):
            for j in range(i + 1, n):
                file_a = all_file_paths[i]
                file_b = all_file_paths[j]
                out = self.detect(file_a, file_b)
                if out["hybrid"]["is_clone"]:
                    results.append({
                        "file_a": file_a,
                        "file_b": file_b,
                        "score": out["hybrid"]["score"],
                        "details": out["hybrid"]["details"]
                    })
        return DetectionResultWrapper(results)

    def get_clone_type(self):
        return "type3"


class DetectionResultWrapper:
    def __init__(self, matches):
        self.clone_groups = matches
        self.total_clones = len(matches)