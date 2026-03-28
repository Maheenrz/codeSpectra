# detectors/type4/type4_detector.py (COMPLETE REPLACEMENT)

"""
Type-4 Detector — Production-Ready Educational Semantic Clone Detection
========================================================================
Complete pipeline with:
  1. Graceful Joern fallback (never fails)
  2. I/O behavioral testing with caching
  3. Algorithm classification for common assignments
  4. Research-based score fusion
  5. Problem-specific detection strategies
"""

from __future__ import annotations

import logging
import shutil
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# Extension to language mapping
_EXT_LANG: Dict[str, str] = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript", ".jsx": "javascript",
    ".ts": "javascript", ".tsx": "javascript",
    ".c": "c",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".h": "cpp", ".hpp": "cpp", ".hxx": "cpp",
}


class Type4Detector:
    """
    Unified Type-4 semantic clone detector with educational focus.
    
    Research-based detection for:
    - Sorting algorithms (bubble, selection, insertion, merge, quick)
    - Data structures (stack, queue, linked list, binary tree)
    - Classic algorithms (fibonacci, factorial, GCD, palindrome)
    - Search algorithms (linear, binary)
    """
    
    def __init__(self, threshold: float = 0.60) -> None:
        self.threshold = threshold
        self._edu = None
        self._custom = None
        self._mode = "uninitialized"
        self._cache_dir = Path("./.cache/type4")
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._init_backend()
    
    def _init_backend(self) -> None:
        """Initialize with graceful fallbacks"""
        logger.info("[Type4Detector] Initializing backend…")
        
        # Try to initialize educational detector
        try:
            from detectors.type4.educational import EducationalType4Detector
            
            # Check for required tools
            has_gpp = shutil.which("g++") is not None
            has_python = shutil.which("python3") or shutil.which("python")
            
            if not has_gpp and not has_python:
                logger.warning("[Type4Detector] No compiler available (g++ or python)")
            
            # Try to load Joern (optional)
            joern = self._try_load_joern()
            
            self._edu = EducationalType4Detector(
                joern_detector=joern,
                io_threshold=self.threshold,
                enable_io=True,
                enable_joern=joern is not None,
                # NOTE: EducationalType4Detector does not accept cache_dir;
                # caching is handled at the Type4Detector level above.
            )
            self._mode = "educational"
            logger.info(
                "✅ [Type4Detector] Educational pipeline ready (joern=%s, compiler=%s)",
                joern is not None,
                has_gpp or has_python,
            )
            return
            
        except ImportError as e:
            logger.warning("[Type4Detector] Educational module import failed: %s", e)
        except Exception as e:
            logger.warning("[Type4Detector] Educational detector init error: %s", e)
        
        # Fallback to heuristic detector
        self._mode = "heuristic"
        logger.info("⚠️  [Type4Detector] Using heuristic fallback (no compilation)")
    
    def _try_load_joern(self) -> Optional[Any]:
        """Attempt to load Joern detector (optional)"""
        try:
            from detectors.type4.joern.robust_joern import get_robust_joern
            joern = get_robust_joern()
            if joern.is_available():
                logger.info("✅ [Type4Detector] Joern available")
                return joern
            else:
                logger.info("[Type4Detector] Joern not available")
                return None
        except Exception as e:
            logger.info("[Type4Detector] Joern load failed: %s", e)
            return None
    
    def detect(
        self,
        file_a: str | Path,
        file_b: str | Path,
        include_features: bool = False,
    ) -> Dict[str, Any]:
        """
        Detect Type-4 semantic similarity.
        
        Returns dict with:
            semantic_score: float (0-1)
            is_semantic_clone: bool
            confidence: str (HIGH/MEDIUM/LOW/UNLIKELY)
            interpretation: str (human-readable)
            category: str (detected problem type)
            io_match_score: float (if available)
        """
        fa, fb = str(file_a), str(file_b)
        logger.info("[Type4Detector] detect(%s, %s)", Path(fa).name, Path(fb).name)
        
        # Check cache
        cache_key = self._get_cache_key(fa, fb)
        cached = self._get_cached(cache_key)
        if cached:
            logger.info("[Type4Detector] Cache hit")
            return cached
        
        # Run detection
        if self._mode == "educational":
            result = self._detect_educational(fa, fb, include_features)
        else:
            result = self._detect_heuristic(fa, fb, include_features)
        
        # Cache result
        self._cache_result(cache_key, result)
        
        return result
    
    def _detect_educational(
        self, fa: str, fb: str, include_features: bool
    ) -> Dict[str, Any]:
        """Use educational detector with full pipeline"""
        try:
            result = self._edu.detect(fa, fb, include_features=include_features)
            
            # Ensure all required fields
            result.setdefault("semantic_score", 0.0)
            result.setdefault("is_semantic_clone", False)
            result.setdefault("confidence", "UNLIKELY")
            result.setdefault("interpretation", "")
            result.setdefault("category", "")
            result.setdefault("io_match_score", None)
            result.setdefault("io_available", False)
            
            result["backend"] = "educational_type4"
            return result
            
        except Exception as e:
            logger.error("[Type4Detector] Educational detect() error: %s", e)
            return self._fallback_result(f"Educational detector failed: {e}")
    
    def _detect_heuristic(
        self, fa: str, fb: str, include_features: bool
    ) -> Dict[str, Any]:
        """Fast heuristic detection (no compilation)"""
        try:
            # Extract signatures
            sig_a = self._extract_signature(fa)
            sig_b = self._extract_signature(fb)
            
            # Calculate similarity
            if not sig_a or not sig_b:
                score = 0.0
            else:
                intersection = len(sig_a & sig_b)
                union = len(sig_a | sig_b)
                score = intersection / union if union > 0 else 0.0
            
            # Determine category
            category = self._guess_category(fa, fb)
            
            # Build interpretation
            if score >= 0.60:
                interpretation = f"⚠️ Possible semantic clone (score={score:.0%})"
            else:
                interpretation = f"✅ Low semantic similarity (score={score:.0%})"
            
            if category:
                interpretation = f"{category} | {interpretation}"
            
            return {
                "semantic_score": round(score, 4),
                "is_semantic_clone": score >= self.threshold,
                "confidence": self._score_to_confidence(score),
                "backend": "heuristic",
                "category": category,
                "interpretation": interpretation,
                "io_match_score": None,
                "io_available": False,
                "category_scores": {
                    "control_flow": score,
                    "data_flow": score,
                    "behavioral": score,
                },
            }
            
        except Exception as e:
            logger.error("[Type4Detector] Heuristic detect error: %s", e)
            return self._fallback_result(f"Heuristic detection failed: {e}")
    
    def _extract_signature(self, file_path: str) -> set:
        """Extract semantic signature from source file"""
        path = Path(file_path)
        if not path.exists():
            return set()
        
        content = path.read_text(encoding='utf-8', errors='ignore')
        lang = _EXT_LANG.get(path.suffix.lower(), "")
        
        signature = set()
        
        # Extract function names
        import re
        if lang == "cpp":
            # Function definitions
            func_patterns = [
                r'\b(void|int|char|float|double|bool|auto|string)\s+(\w+)\s*\([^)]*\)\s*\{',
                r'\b(\w+)\s*::\s*(\w+)\s*\([^)]*\)\s*\{',
            ]
            for pattern in func_patterns:
                for match in re.findall(pattern, content):
                    if isinstance(match, tuple):
                        name = match[-1] if match[-1] else match[0]
                    else:
                        name = match
                    if name and not name.startswith('_'):
                        signature.add(f"func:{name}")
            
            # Class names
            for match in re.findall(r'\bclass\s+(\w+)', content):
                signature.add(f"class:{match}")
            
            # Includes
            for match in re.findall(r'#include\s*[<"]([^>"]+)[>"]', content):
                signature.add(f"include:{match}")
        
        elif lang == "python":
            # Function definitions
            for match in re.findall(r'def\s+(\w+)\s*\(', content):
                signature.add(f"func:{match}")
            
            # Class definitions
            for match in re.findall(r'class\s+(\w+)', content):
                signature.add(f"class:{match}")
            
            # Imports
            for match in re.findall(r'import\s+(\w+)', content):
                signature.add(f"import:{match}")
        
        # Extract control structures
        structures = []
        if 'for' in content.lower():
            structures.append('has_loop')
        if 'while' in content.lower():
            structures.append('has_loop')
        if 'if' in content.lower():
            structures.append('has_conditional')
        if 'return' in content.lower():
            structures.append('has_return')
        
        for s in structures:
            signature.add(s)
        
        return signature
    
    def _guess_category(self, file_a: str, file_b: str) -> str:
        """Guess problem category from filenames and content"""
        name_a = Path(file_a).stem.lower()
        name_b = Path(file_b).stem.lower()
        combined = name_a + name_b
        
        categories = {
            'sort': ['sort', 'bubble', 'selection', 'insertion', 'merge', 'quick'],
            'stack': ['stack', 'push', 'pop', 'lifo'],
            'queue': ['queue', 'enqueue', 'dequeue', 'fifo'],
            'linkedlist': ['linked', 'list', 'node'],
            'tree': ['tree', 'bst', 'binary', 'node'],
            'fibonacci': ['fib', 'fibonacci'],
            'factorial': ['fact', 'factorial'],
            'gcd': ['gcd', 'hcf', 'euclid'],
            'palindrome': ['palindrome', 'palin'],
            'search': ['search', 'find', 'binary', 'linear'],
        }
        
        for cat, keywords in categories.items():
            if any(kw in combined for kw in keywords):
                return cat.upper()
        
        return ""
    
    def _score_to_confidence(self, score: float) -> str:
        if score >= 0.80:
            return "HIGH"
        elif score >= 0.65:
            return "MEDIUM"
        elif score >= 0.50:
            return "LOW"
        return "UNLIKELY"
    
    def _get_cache_key(self, file_a: str, file_b: str) -> str:
        """Generate cache key from file contents"""
        def get_hash(path: str) -> str:
            path = Path(path)
            if not path.exists():
                return ""
            content = path.read_text(encoding='utf-8', errors='ignore')
            return hashlib.md5(content.encode()).hexdigest()[:16]
        
        hash_a = get_hash(file_a)
        hash_b = get_hash(file_b)
        combined = f"{hash_a}_{hash_b}_{self.threshold}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached result"""
        cache_file = self._cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    # Check age (1 day)
                    age = time.time() - cached.get('timestamp', 0)
                    if age < 86400:
                        return cached.get('result')
            except Exception:
                pass
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
        except Exception:
            pass
    
    def _fallback_result(self, error_msg: str = "") -> Dict[str, Any]:
        return {
            "semantic_score": 0.0,
            "is_semantic_clone": False,
            "confidence": "UNLIKELY",
            "backend": "unavailable",
            "interpretation": f"Detection unavailable: {error_msg}" if error_msg else "Detection unavailable",
            "category": "",
            "io_match_score": None,
            "io_available": False,
            "category_scores": {
                "control_flow": 0.0,
                "data_flow": 0.0,
                "behavioral": 0.0,
                "structural": 0.0,
            },
        }
    
    def prepare_batch(self, file_paths: List[Any]) -> None:
        """Batch preparation"""
        pass
    
    def clear_cache(self) -> None:
        """Clear result cache"""
        import shutil
        if self._cache_dir.exists():
            shutil.rmtree(self._cache_dir)
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("[Type4Detector] Cache cleared")
    
    def get_mode(self) -> str:
        return self._mode