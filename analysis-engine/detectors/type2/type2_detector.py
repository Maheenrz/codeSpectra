# detectors/type2/type2_detector.py
"""
Type-2 Clone Detector — STUB.

(normalized token / renamed-variable comparison).

The interface MUST stay the same:
    detect(file_a: str, file_b: str) → dict with keys:
        type2_score: float   (0.0 – 1.0)
        is_clone:    bool
        confidence:  str     (HIGH / MEDIUM / LOW / UNLIKELY / PENDING)
"""
from typing import Any, Dict


class Type2Detector:
    """
    Detects renamed-variable clones (same structure, different identifiers).
    *** NOT YET IMPLEMENTED — returns 0.0 until teammate fills this in. ***
    """

    def detect(self, file_a: str, file_b: str) -> Dict[str, Any]:
        # ── TODO: implement real Type-2 detection here ──────────────────────
        # Suggested approach:
        #   1. Tokenize both files with pygments
        #   2. Normalize: replace all identifiers → "ID", literals → "LIT"
        #   3. Compute Jaccard / sequence similarity on the normalised token stream
        #   4. Return score + confidence
        # ────────────────────────────────────────────────────────────────────
        return {
            "type2_score": 0.0,
            "is_clone":    False,
            "confidence":  "PENDING",
            "note":        "Type-2 detection not yet implemented",
        }