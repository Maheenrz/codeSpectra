# detectors/type1/type1_detector.py
"""
Type-1 Clone Detector — file-level adapter.
Wraps existing hash/string methods into the same detect(file_a, file_b) API
used by Type-3 and Type-4 detectors.
"""
import difflib
import hashlib
import re
from pathlib import Path
from typing import Any, Dict


class Type1Detector:
    """
    Detects exact and near-exact (whitespace/comment-only changes) clones.
    Score 1.0 = identical after normalization.
    Score ≥ 0.95 = near-exact (Type-1 clone).
    """

    def _normalize(self, code: str) -> str:
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'#.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        return re.sub(r'\s+', ' ', code).strip().lower()

    def detect(self, file_a: str, file_b: str) -> Dict[str, Any]:
        try:
            code_a = Path(file_a).read_text(encoding='utf-8', errors='ignore')
            code_b = Path(file_b).read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"type1_score": 0.0, "is_clone": False,
                    "confidence": "ERROR", "error": str(e)}

        norm_a = self._normalize(code_a)
        norm_b = self._normalize(code_b)

        if not norm_a or not norm_b:
            return {"type1_score": 0.0, "is_clone": False, "confidence": "EMPTY"}

        # Exact hash match
        if (hashlib.sha256(norm_a.encode()).hexdigest() ==
                hashlib.sha256(norm_b.encode()).hexdigest()):
            return {"type1_score": 1.0, "is_clone": True, "confidence": "EXACT"}

        # Near-exact via difflib
        ratio = round(difflib.SequenceMatcher(None, norm_a, norm_b).ratio(), 4)
        is_clone = ratio >= 0.95

        if ratio >= 0.99:
            confidence = "HIGH"
        elif ratio >= 0.95:
            confidence = "MEDIUM"
        elif ratio >= 0.80:
            confidence = "LOW"
        else:
            confidence = "UNLIKELY"

        return {"type1_score": ratio, "is_clone": is_clone, "confidence": confidence}