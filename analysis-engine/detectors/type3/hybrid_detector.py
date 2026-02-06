# analysis-engine/detectors/type3/hybrid_detector.py
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

DETECTOR_DIR = Path(__file__).resolve().parent
REPO_ROOT = DETECTOR_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT / "analysis-engine"))

from core.ast_ml_adapter import ASTMLAdapter


class Type3HybridDetector:
    """
    Hybrid detector with unified model trained on BigCloneBench (Java).
    Works for: Java, C++, C, Python (transfer learning approach).
    
    Detection Strategy:
    - Combined score = (hybrid * 0.5) + (ml * 0.5)
    - Uses AND logic: Both hybrid AND ml must agree for high confidence
    - Provides confidence levels: HIGH, MEDIUM, LOW, UNLIKELY
    """
    
    # Language-specific thresholds (RAISED for better precision)
    LANGUAGE_THRESHOLDS = {
        'java': {'hybrid': 0.50, 'ml': 0.60, 'combined': 0.55},
        'cpp': {'hybrid': 0.50, 'ml': 0.60, 'combined': 0.55},
        'c': {'hybrid': 0.50, 'ml': 0.60, 'combined': 0.55},
        'python': {'hybrid': 0.55, 'ml': 0.65, 'combined': 0.60},
        'javascript': {'hybrid': 0.50, 'ml': 0.60, 'combined': 0.55},
    }
    
    # Confidence level thresholds
    CONFIDENCE_LEVELS = {
        'HIGH': 0.75,      # Very likely a clone
        'MEDIUM': 0.55,    # Probably a clone, needs review
        'LOW': 0.40,       # Suspicious, might be coincidence
        'UNLIKELY': 0.0    # Probably not a clone
    }
    
    def __init__(self, hybrid_threshold: float = 0.50, ml_threshold: float = 0.60):
        # Heuristic components
        self.tokenizer = CodeTokenizer()
        self.metrics_calc = MetricsCalculator()
        self.ast_processor = ASTProcessor()
        self.winnowing = WinnowingDetector(k=5, window_size=4)
        self.freq_filter = BatchFrequencyFilter(threshold=0.7)

        # ML components
        self.default_hybrid_threshold = hybrid_threshold
        self.default_ml_threshold = ml_threshold
        self.default_combined_threshold = 0.55
        self.adapter = ASTMLAdapter(cache_dir=str(REPO_ROOT / "analysis-engine" / "feature_cache"))
        self.models_dir = DETECTOR_DIR / "models"

        self.ml_enabled = False
        self.feature_names: List[str] = []
        self.clf = None
        self.language_thresholds = self.LANGUAGE_THRESHOLDS.copy()

        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the trained ML model"""
        
        # Try unified model first (new approach - trained on BigCloneBench)
        unified_model = self.models_dir / "type3_unified_model.joblib"
        unified_names = self.models_dir / "type3_unified_model.names.json"
        unified_meta = self.models_dir / "type3_unified_model.meta.json"

        if unified_model.exists() and unified_names.exists():
            print("✅ Loading unified model (trained on BigCloneBench)")
            self.clf = joblib.load(unified_model)
            self.feature_names = json.loads(unified_names.read_text())
            self.ml_enabled = True
            
            # Load metadata but use our improved thresholds
            if unified_meta.exists():
                meta = json.loads(unified_meta.read_text())
                # We don't override thresholds from meta anymore
                # Using our improved LANGUAGE_THRESHOLDS instead
            return

        # Fallback to legacy model
        legacy_model = self.models_dir / "type3_rf_features.joblib"
        legacy_names = self.models_dir / "type3_rf_features.names.json"
        
        if legacy_model.exists() and legacy_names.exists():
            print("⚠️ Using legacy model (consider retraining with new pipeline)")
            self.clf = joblib.load(legacy_model)
            self.feature_names = json.loads(legacy_names.read_text())
            self.ml_enabled = True
            return

        print("⚠️ No ML model found. Using heuristics only.")
        self.ml_enabled = False
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect language from file extension"""
        ext = file_path.suffix.lower()
        ext_map = {
            '.java': 'java',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
            '.c': 'c', '.h': 'c',
            '.hpp': 'cpp',
            '.py': 'python',
            '.js': 'javascript', '.ts': 'javascript',
        }
        return ext_map.get(ext, 'cpp')
    
    def _get_thresholds(self, language: str) -> dict:
        """Get language-specific thresholds"""
        default = {
            'hybrid': self.default_hybrid_threshold,
            'ml': self.default_ml_threshold,
            'combined': self.default_combined_threshold
        }
        return self.language_thresholds.get(language, default)
    
    def _get_confidence_level(self, combined_score: float) -> str:
        """Determine confidence level based on combined score"""
        if combined_score >= self.CONFIDENCE_LEVELS['HIGH']:
            return 'HIGH'
        elif combined_score >= self.CONFIDENCE_LEVELS['MEDIUM']:
            return 'MEDIUM'
        elif combined_score >= self.CONFIDENCE_LEVELS['LOW']:
            return 'LOW'
        else:
            return 'UNLIKELY'

    def prepare_batch(self, all_file_paths: List[Path]):
        """
        Train the frequency filter on the whole batch to remove common boilerplate.
        Must be called BEFORE detect() for correct Winnowing behavior.
        """
        all_tokens = [self.tokenizer.tokenize_file(str(p)) for p in all_file_paths]
        self.freq_filter.train_on_batch(all_tokens)

    def _hybrid_scores(self, file_a: Path, file_b: Path) -> Dict[str, float]:
        """Calculate hybrid heuristic scores"""
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

        # AST skeleton similarity
        a_score = float(self.ast_processor.calculate_similarity(str(file_a), str(file_b)))

        # Complexity metrics similarity
        ma = self.metrics_calc.calculate_file_metrics(str(file_a))
        mb = self.metrics_calc.calculate_file_metrics(str(file_b))
        m_score = float(self.metrics_calc.calculate_similarity(ma, mb))

        return {"winnowing": w_score, "ast": a_score, "metrics": m_score}

    def _select_primary_unit(self, units: List) -> Optional[Any]:
        """Select the primary/main unit from a list of units"""
        if not units:
            return None
            
        for u in units:
            try:
                self.adapter.normalize_unit(u)
                self.adapter.compute_ast_counts(u)
            except Exception:
                pass
        
        # Prefer common function names
        preferred = {"maxSubArray", "solve", "solution", "main", "Solution"}
        named = [u for u in units if getattr(u, "func_name", "") in preferred]
        
        if named:
            named.sort(key=lambda x: (x.features or {}).get("token_count", 0), reverse=True)
            return named[0]
        
        # Otherwise return largest unit
        units.sort(key=lambda x: (x.features or {}).get("token_count", 0), reverse=True)
        return units[0]

    def _ml_vec(self, file_a: Path, file_b: Path) -> Optional[np.ndarray]:
        """Extract ML feature vector for a pair of files"""
        try:
            units_a = self.adapter.build_units_from_file(str(file_a))
            units_b = self.adapter.build_units_from_file(str(file_b))
            
            if not units_a or not units_b:
                return None
            
            ua = self._select_primary_unit(units_a)
            ub = self._select_primary_unit(units_b)
            
            if ua is None or ub is None:
                return None

            # Process units
            self.adapter.normalize_unit(ua)
            self.adapter.normalize_unit(ub)
            self.adapter.compute_subtree_hashes(ua)
            self.adapter.compute_subtree_hashes(ub)
            self.adapter.extract_ast_paths(ua)
            self.adapter.extract_ast_paths(ub)
            self.adapter.compute_ast_counts(ua)
            self.adapter.compute_ast_counts(ub)
            
            # TF-IDF for cosine similarity
            self.adapter.vectorize_units([ua], method="tfidf")
            self.adapter.vectorize_units([ub], method="tfidf")

            # Get pair features
            feats = self.adapter.make_pair_features(ua, ub)
            fa = ua.features or {}
            fb = ub.features or {}
            
            feature_map = {
                "jaccard_subtrees": feats.get("jaccard_subtrees", 0.0),
                "cosine_paths": feats.get("cosine_paths", 0.0),
                "abs_token_count_diff": feats.get("abs_token_count_diff", 0.0),
                "avg_token_count": feats.get("avg_token_count", 0.0),
                "subtree_count_A": len(ua.subtree_hashes or set()),
                "subtree_count_B": len(ub.subtree_hashes or set()),
                "path_count_A": len(ua.ast_paths or []),
                "path_count_B": len(ub.ast_paths or []),
                "token_count_A": fa.get("token_count", 0),
                "token_count_B": fb.get("token_count", 0),
                "call_approx_A": fa.get("call_approx", 0),
                "call_approx_B": fb.get("call_approx", 0),
            }
            
            # Build vector in correct order
            vec = np.array(
                [float(feature_map.get(n, 0.0)) for n in self.feature_names],
                dtype=np.float32
            )
            return vec
            
        except Exception as e:
            print(f"⚠️ ML feature extraction failed: {e}")
            return None

    def detect(self, file_path_a: str | Path, file_path_b: str | Path) -> Dict[str, Any]:
        """
        Main detection method with language-aware thresholds and combined scoring.
        
        Returns:
            {
                "hybrid": {"score": float, "is_clone": bool, "details": {...}},
                "ml": {"score": float, "is_clone": bool, "threshold_used": float},
                "combined": {"score": float, "is_clone": bool, "confidence": str},
                "is_clone": bool,  # Final verdict using AND logic
                "language": str,
                "thresholds": {"hybrid": float, "ml": float, "combined": float}
            }
        """
        file_a = Path(file_path_a)
        file_b = Path(file_path_b)
        
        # Detect language and get thresholds
        language = self._detect_language(file_a)
        thresholds = self._get_thresholds(language)

        # Hybrid heuristics
        h = self._hybrid_scores(file_a, file_b)
        hybrid_score = (h["winnowing"] * 0.3) + (h["ast"] * 0.6) + (h["metrics"] * 0.1)
        
        hybrid = {
            "score": round(hybrid_score, 4),
            "is_clone": bool(hybrid_score >= thresholds['hybrid']),
            "details": {
                "winnowing_fingerprint_score": round(h["winnowing"], 4),
                "ast_skeleton_score": round(h["ast"], 4),
                "complexity_metric_score": round(h["metrics"], 4),
            },
        }

        # ML prediction
        ml_score = 0.0
        ml = None
        if self.ml_enabled and self.clf is not None:
            vec = self._ml_vec(file_a, file_b)
            
            if vec is not None and vec.size > 0:
                vec = vec.reshape(1, -1)
                
                if hasattr(self.clf, "predict_proba"):
                    ml_score = float(self.clf.predict_proba(vec)[0][1])
                    ml = {
                        "score": round(ml_score, 4),
                        "is_clone": bool(ml_score >= thresholds['ml']),
                        "threshold_used": thresholds['ml']
                    }
                else:
                    pred = int(self.clf.predict(vec)[0])
                    ml_score = float(pred)
                    ml = {
                        "score": ml_score,
                        "is_clone": bool(pred == 1),
                        "threshold_used": thresholds['ml']
                    }

        # ============================================
        # COMBINED SCORE (NEW!)
        # ============================================
        # Weighted combination of hybrid and ML scores
        if ml is not None:
            combined_score = (hybrid_score * 0.5) + (ml_score * 0.5)
        else:
            # If ML not available, use only hybrid
            combined_score = hybrid_score
        
        combined_is_clone = bool(combined_score >= thresholds['combined'])
        confidence = self._get_confidence_level(combined_score)
        
        combined = {
            "score": round(combined_score, 4),
            "is_clone": combined_is_clone,
            "confidence": confidence
        }

        # ============================================
        # FINAL VERDICT (Using AND logic for high precision)
        # ============================================
        # Clone only if BOTH hybrid AND ml agree (when ml is available)
        if ml is not None:
            # AND logic: Both must say it's a clone
            final_is_clone = hybrid["is_clone"] and ml["is_clone"]
        else:
            # If ML not available, use hybrid only
            final_is_clone = hybrid["is_clone"]
        
        # Alternative: Use combined score for final verdict
        # Uncomment below if you prefer combined score over AND logic
        # final_is_clone = combined_is_clone

        return {
            "hybrid": hybrid,
            "ml": ml,
            "combined": combined,
            "is_clone": final_is_clone,  # FINAL VERDICT
            "language": language,
            "thresholds": thresholds
        }

    def detect_clones(self, all_file_paths: List[str]):
        """
        Batch detection for compatibility with detection engine.
        Returns results sorted by combined score (highest first).
        """
        results = []
        n = len(all_file_paths)
        self.prepare_batch([Path(p) for p in all_file_paths])

        for i in range(n):
            for j in range(i + 1, n):
                file_a = all_file_paths[i]
                file_b = all_file_paths[j]
                out = self.detect(file_a, file_b)
                
                # Use the final verdict (AND logic)
                is_clone = out["is_clone"]
                
                # Only include if it's a clone OR has medium+ confidence
                # This allows reviewing suspicious pairs too
                combined_score = out["combined"]["score"]
                confidence = out["combined"]["confidence"]
                
                if is_clone or confidence in ['HIGH', 'MEDIUM']:
                    results.append({
                        "file_a": file_a,
                        "file_b": file_b,
                        "is_clone": is_clone,
                        "hybrid_score": out["hybrid"]["score"],
                        "ml_score": out["ml"]["score"] if out["ml"] else None,
                        "combined_score": combined_score,
                        "confidence": confidence,
                        "language": out["language"],
                        "details": out["hybrid"]["details"]
                    })
        
        # Sort by combined score (highest first)
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return DetectionResultWrapper(results)

    def get_clone_type(self):
        return "type3"


class DetectionResultWrapper:
    """Wrapper for detection results"""
    def __init__(self, matches):
        self.clone_groups = matches
        self.total_clones = len([m for m in matches if m.get("is_clone", False)])
        self.total_suspicious = len(matches)
        
    def get_high_confidence_clones(self):
        """Get only HIGH confidence clones"""
        return [m for m in self.clone_groups if m.get("confidence") == "HIGH"]
    
    def get_clones_by_confidence(self, confidence: str):
        """Get clones by confidence level"""
        return [m for m in self.clone_groups if m.get("confidence") == confidence]