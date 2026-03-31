# detectors/type4/educational/educational_detector.py
"""
Educational Type-4 Detector — Production-Ready with Caching and Research-Based Fusion
"""

from __future__ import annotations

import logging
import time
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from .algorithm_classifier import get_classifier, ClassificationResult
from .io_behavioral_tester import get_tester, IOBehavioralResult
from .score_fusion import FusionInput, FusionResult, fuse_scores

logger = logging.getLogger(__name__)


class EducationalType4Detector:
    """
    Complete educational Type-4 semantic clone detector with:
    - Caching for performance
    - Graceful fallbacks
    - Research-based score fusion
    - Student-friendly output normalization
    """

    def __init__(
        self,
        joern_detector=None,
        io_threshold: float = 0.60,
        max_test_cases: int = 15,
        enable_io: bool = True,
        enable_joern: bool = True,
        cache_dir: str = "./.cache/type4",
    ) -> None:
        self._joern = joern_detector
        self._threshold = io_threshold
        self._enable_io = enable_io
        self._enable_joern = enable_joern and joern_detector is not None
        self._classifier = get_classifier()
        self._io_tester = get_tester()
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Research-based weights (BigCloneBench + NiCad)
        self.WEIGHTS = {
            'pdg': 0.35,      # Structural/control flow
            'io': 0.45,       # Behavioral equivalence (MOST IMPORTANT)
            'signature': 0.20 # Static algorithm signature
        }
        
        logger.info(
            "[EduDetector] Initialized | joern=%s io=%s threshold=%.2f cache=%s",
            self._enable_joern, self._enable_io, self._threshold, self._cache_dir,
        )

    # ─── Public API ──────────────────────────────────────────────────────────

    def detect(
        self,
        file_a: str,
        file_b: str,
        include_features: bool = False,
    ) -> Dict[str, Any]:
        """
        Detect semantic clones with caching.
        
        Args:
            file_a: Path to first source file
            file_b: Path to second source file
            include_features: Include detailed diagnostic info
            
        Returns:
            Detection result dict
        """
        # Check cache
        cache_key = self._get_cache_key(file_a, file_b)
        cached = self._get_cached(cache_key)
        if cached:
            logger.info("[EduDetector] Cache hit for %s vs %s", 
                       Path(file_a).name, Path(file_b).name)
            return cached
        
        # Run detection
        result = self._detect_internal(file_a, file_b, include_features)
        
        # Cache result
        self._cache_result(cache_key, result)
        
        return result

    def prepare_batch(self, file_paths: List[Any]) -> None:
        """No-op for API compatibility"""
        pass

    def clear_cache(self) -> None:
        """Clear the cache directory"""
        import shutil
        if self._cache_dir.exists():
            shutil.rmtree(self._cache_dir)
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("[EduDetector] Cache cleared")

    # ─── Internal Detection ──────────────────────────────────────────────────

    def _detect_internal(
        self, 
        file_a: str, 
        file_b: str, 
        include_features: bool
    ) -> Dict[str, Any]:
        """Internal detection logic"""
        t_start = time.time()
        name_a = Path(file_a).name
        name_b = Path(file_b).name
        logger.info("[EduDetector] Detecting: %s vs %s", name_a, name_b)
        
        try:
            # Collect all signals
            signals = self._collect_signals(file_a, file_b)
            
            # Fuse signals
            final_score = self._fuse_signals(signals)
            
            # Determine clone status
            is_clone = final_score >= self._threshold
            confidence = self._determine_confidence(final_score, signals)
            
            # Build result
            result = {
                "semantic_score": round(final_score, 4),
                "is_semantic_clone": is_clone,
                "confidence": confidence,
                "backend": "educational_type4",
                "category": signals.get('category', ''),
                "interpretation": self._generate_interpretation(
                    final_score, confidence, signals
                ),
                "io_match_score": signals.get('io_score'),
                "io_available": signals.get('io_available', False),
                "category_scores": {
                    "control_flow": round(signals.get('pdg_score', 0), 4),
                    "data_flow": round(signals.get('pdg_score', 0), 4),
                    "behavioral": round(signals.get('io_score', 0), 4),
                    "structural": round(signals.get('signature_score', 0), 4),
                },
            }
            
            elapsed_ms = round((time.time() - t_start) * 1000, 2)
            logger.info(
                "[EduDetector] Done in %dms: score=%.3f clone=%s confidence=%s",
                elapsed_ms, final_score, is_clone, confidence
            )
            
            return result
            
        except Exception as e:
            logger.exception("[EduDetector] Detection failed: %s", e)
            return self._fallback_result(str(e))

    # ─── Signal Collection ───────────────────────────────────────────────────

    def _collect_signals(self, file_a: str, file_b: str) -> Dict:
        """Collect all signals with graceful degradation"""
        signals = {
            # Use 0.0 as the "no evidence" default, not 0.5.
            # 0.5 would create a phantom 50% Type-4 score on every pair
            # even when no Joern PDG and no I/O test ran.
            'pdg_score': 0.0,
            'pdg_available': False,
            'signature_score': 0.0,   # overwritten below if classifier succeeds
            'io_available': False,
            'category': '',
        }
        
        # Signal 1: PDG (if available)
        if self._enable_joern and self._joern:
            try:
                if hasattr(self._joern, 'detect'):
                    pdg_score, _ = self._joern.detect(file_a, file_b)
                    signals['pdg_score'] = pdg_score
                    signals['pdg_available'] = True
                    logger.debug(f"[EduDetector] PDG score: {pdg_score:.3f}")
            except Exception as e:
                logger.warning(f"[EduDetector] PDG failed: {e}")
        
        # Signal 2: I/O behavioral
        if self._enable_io:
            try:
                io_result = self._io_tester.test(file_a, file_b)
                if io_result.succeeded and io_result.io_match_score is not None:
                    signals['io_score'] = io_result.io_match_score
                    signals['io_available'] = True
                    signals['mutual_correctness'] = io_result.mutual_correctness
                    if io_result.category:
                        signals['category'] = io_result.category
                    logger.debug(f"[EduDetector] I/O score: {io_result.io_match_score:.3f}")
                else:
                    logger.debug(f"[EduDetector] I/O skipped: {io_result.error_message}")
            except Exception as e:
                logger.warning(f"[EduDetector] I/O failed: {e}")
        
        # Signal 3: Algorithm signature
        try:
            cls_a = self._classifier.classify_file(file_a)
            cls_b = self._classifier.classify_file(file_b)
            
            if cls_a.is_known and cls_b.is_known:
                if cls_a.category == cls_b.category:
                    if cls_a.algorithm_family == cls_b.algorithm_family:
                        # Same problem, same algorithm variant— strong clone signal
                        signals['signature_score'] = 1.0
                        logger.debug("[EduDetector] Same algorithm family")
                    else:
                        # Same problem, different variant (e.g. bubble vs selection sort)
                        signals['signature_score'] = 0.7
                        logger.debug("[EduDetector] Same category, different algorithm")
                else:
                    # Different problems entirely — very unlikely to be a clone
                    signals['signature_score'] = 0.1
                    logger.debug("[EduDetector] Different categories")
            elif cls_a.is_known or cls_b.is_known:
                # One file classified, the other unknown — weak signal
                signals['signature_score'] = 0.3
                logger.debug("[EduDetector] Partial classification")
            else:
                # Neither file classified — neutral (classifier ran but found nothing)
                signals['signature_score'] = 0.5
                logger.debug("[EduDetector] Unknown category (both files unclassified)")
            
            if not signals['category'] and cls_a.is_known:
                signals['category'] = cls_a.category
                
        except Exception as e:
            logger.warning(f"[EduDetector] Classifier failed: {e}")
        
        return signals

    # ─── Score Fusion ────────────────────────────────────────────────────────

    def _fuse_signals(self, signals: Dict) -> float:
        """Fuse signals with research-based weights"""
        if signals.get('io_available', False):
            # Full fusion
            score = (
                signals.get('pdg_score', 0.5) * self.WEIGHTS['pdg'] +
                signals.get('io_score', 0) * self.WEIGHTS['io'] +
                signals.get('signature_score', 0.5) * self.WEIGHTS['signature']
            )
        else:
            # No I/O - rely on PDG + signature
            adjusted_weights = {'pdg': 0.60, 'signature': 0.40}
            score = (
                signals.get('pdg_score', 0.5) * adjusted_weights['pdg'] +
                signals.get('signature_score', 0.5) * adjusted_weights['signature']
            )
        
        # Boost for mutual correctness (both produce correct output)
        if signals.get('mutual_correctness', 0) > 0.8:
            score = min(score * 1.1, 1.0)
            logger.debug("[EduDetector] Applied mutual correctness boost")
        
        return min(max(score, 0.0), 1.0)

    def _determine_confidence(self, score: float, signals: Dict) -> str:
        """Determine confidence level based on research"""
        if score >= 0.85:
            return "HIGH"
        elif score >= 0.70:
            if signals.get('io_available', False) and signals.get('io_score', 0) >= 0.8:
                return "HIGH"  # I/O confirmation
            return "MEDIUM"
        elif score >= 0.55:
            return "LOW"
        return "UNLIKELY"

    # ─── Interpretation ──────────────────────────────────────────────────────

    def _generate_interpretation(self, score: float, confidence: str, signals: Dict) -> str:
        """Generate human-readable interpretation for teachers"""
        parts = []
        
        # Category
        if signals.get('category'):
            category_display = {
                'SORT_ARRAY': 'Sorting Algorithm',
                'STACK_OOP': 'Stack (OOP)',
                'STACK_PROCEDURAL': 'Stack (Procedural)',
                'LINKED_LIST': 'Linked List',
                'LINEAR_SEARCH': 'Linear Search',
                'BINARY_SEARCH': 'Binary Search',
                'FIBONACCI': 'Fibonacci',
                'FACTORIAL': 'Factorial',
                'GCD': 'GCD/Euclidean Algorithm',
                'IS_PALINDROME': 'Palindrome Check',
                'STRING_REVERSE': 'String Reverse',
            }.get(signals['category'], signals['category'])
            parts.append(f"📚 {category_display}")
        
        # I/O result
        if signals.get('io_available', False):
            io_pct = signals.get('io_score', 0) * 100
            parts.append(f"✅ I/O match: {io_pct:.0f}%")
        
        # PDG result
        if signals.get('pdg_available', False):
            pdg_pct = signals.get('pdg_score', 0) * 100
            parts.append(f"🏗️ Structure: {pdg_pct:.0f}%")
        
        # Signature result
        sig_pct = signals.get('signature_score', 0) * 100
        if sig_pct >= 80:
            parts.append(f"🔍 Same algorithm")
        elif sig_pct >= 50:
            parts.append(f"📖 Similar approach")
        
        # Verdict
        if score >= 0.70:
            parts.append(f"⚠️ Semantic clone detected ({score:.0%}, {confidence})")
        elif score >= 0.55:
            parts.append(f"📋 Possible semantic clone ({score:.0%}, {confidence})")
        else:
            parts.append(f"✅ Not a semantic clone ({score:.0%})")
        
        return " | ".join(parts)

    # ─── Caching ────────────────────────────────────────────────────────────

    def _get_cache_key(self, file_a: str, file_b: str) -> str:
        """Generate cache key from file contents"""
        def get_hash(path: str) -> str:
            path = Path(path)
            if not path.exists():
                return ""
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
                return hashlib.md5(content.encode()).hexdigest()[:16]
            except Exception:
                return ""
        
        hash_a = get_hash(file_a)
        hash_b = get_hash(file_b)
        combined = f"{hash_a}_{hash_b}_{self._threshold}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached result"""
        cache_file = self._cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    age = time.time() - cached.get('timestamp', 0)
                    if age < 86400:  # 24 hours
                        return cached.get('result')
            except Exception as e:
                logger.debug(f"[EduDetector] Cache read failed: {e}")
        return None

    def _cache_result(self, key: str, result: Dict) -> None:
        """Cache result"""
        cache_file = self._cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'result': result
                }, f)
        except Exception as e:
            logger.debug(f"[EduDetector] Cache write failed: {e}")

    # ─── Fallback ───────────────────────────────────────────────────────────

    def _fallback_result(self, error_msg: str) -> Dict[str, Any]:
        """Return safe fallback result on error"""
        return {
            "semantic_score": 0.0,
            "is_semantic_clone": False,
            "confidence": "UNLIKELY",
            "backend": "educational_type4",
            "category": "",
            "interpretation": f"⚠️ Detection unavailable: {error_msg[:100]}",
            "io_match_score": None,
            "io_available": False,
            "category_scores": {
                "control_flow": 0.0,
                "data_flow": 0.0,
                "behavioral": 0.0,
                "structural": 0.0,
            },
        }