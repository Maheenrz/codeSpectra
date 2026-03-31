"""
Robust Joern wrapper with graceful fallback for educational use
"""

import logging
import re
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class RobustJoernDetector:
    """
    Joern detector that never fails - falls back to heuristic analysis
    """
    
    def __init__(self, auto_start: bool = True):
        self._joern = None
        self._available = False
        
        try:
            from .joern_detector import JoernDetector
            self._joern = JoernDetector(auto_start=auto_start)
            status = self._joern.get_status()
            if status.get('container_running') and status.get('docker_available'):
                self._available = True
                logger.info("✅ RobustJoern: Joern available")
            else:
                logger.info("RobustJoern: Joern not available, using heuristic")
        except Exception as e:
            logger.info(f"RobustJoern: Joern init failed ({e}), using heuristic")
    
    def is_available(self) -> bool:
        return self._available
    
    def detect(self, file_a: str, file_b: str, language: str = "cpp") -> Tuple[float, float]:
        """
        Detect similarity with fallback
        Returns:
            (similarity, confidence)
        """
        if self._available:
            try:
                result = self._joern.detect_from_files(file_a, file_b)
                if result.status == "success":
                    return result.similarity, self._confidence_to_score(result.confidence.value)
            except Exception as e:
                logger.warning(f"Joern detection failed: {e}")
        # Fallback: heuristic
        return self._heuristic_similarity(file_a, file_b, language), 0.6
    
    def _heuristic_similarity(self, file_a: str, file_b: str, language: str) -> float:
        """Quick heuristic similarity"""
        try:
            content_a = Path(file_a).read_text(encoding='utf-8', errors='ignore')
            content_b = Path(file_b).read_text(encoding='utf-8', errors='ignore')
            # Extract function signatures
            sig_a = self._extract_signatures(content_a, language)
            sig_b = self._extract_signatures(content_b, language)
            if not sig_a and not sig_b:
                return 0.5
            if not sig_a or not sig_b:
                return 0.3
            # Jaccard similarity
            intersection = len(sig_a & sig_b)
            union = len(sig_a | sig_b)
            return intersection / union if union > 0 else 0.0
        except Exception as e:
            logger.debug(f"Heuristic similarity failed: {e}")
            return 0.5
    
    def _extract_signatures(self, content: str, language: str) -> set:
        """Extract function signatures"""
        signatures = set()
        if language in ("cpp", "c"):
            patterns = [
                r'\b(void|int|char|float|double|bool|auto|string|long|short)\s+(\w+)\s*\([^)]*\)\s*\{',
                r'\b(\w+)\s*::\s*(\w+)\s*\([^)]*\)\s*\{',
                r'^\s*(\w+)\s*\([^)]*\)\s*\{',
            ]
            for pattern in patterns:
                for match in re.findall(pattern, content, re.MULTILINE):
                    if isinstance(match, tuple):
                        name = match[-1] if match[-1] else match[0]
                    else:
                        name = match
                    if name and not name.startswith('_') and len(name) > 1:
                        signatures.add(f"func:{name}")
        elif language == "python":
            for match in re.findall(r'def\s+(\w+)\s*\(', content):
                signatures.add(f"func:{match}")
        elif language in ("javascript", "js"):
            for match in re.findall(r'function\s+(\w+)\s*\(', content):
                signatures.add(f"func:{match}")
            for match in re.findall(r'const\s+(\w+)\s*=\s*\(', content):
                signatures.add(f"func:{match}")
        return signatures
    
    def _confidence_to_score(self, confidence: str) -> float:
        mapping = {"high": 0.9, "medium": 0.7, "low": 0.5}
        return mapping.get(confidence.lower(), 0.5)

# Singleton
_robust_joern = None

def get_robust_joern() -> RobustJoernDetector:
    global _robust_joern
    if _robust_joern is None:
        _robust_joern = RobustJoernDetector()
    return _robust_joern
