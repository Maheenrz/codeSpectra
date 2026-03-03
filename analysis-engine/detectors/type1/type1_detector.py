# detectors/type1/type1_detector.py
"""
Type-1 Clone Detector — Exact Clone Detection
===============================================

Type-1 clones per Roy & Cordy (2008):
  Identical code fragments except for differences in whitespace,
  layout, and comments.

Key principles:
  - Preserve case (MyVar ≠ myvar — that's a Type-2 change)
  - Preserve identifiers exactly (rename = Type-2, not Type-1)
  - Only strip comments and normalize whitespace
  - Use hash-first for speed, then SequenceMatcher for near-exact

Detection logic:
  1. Read both files
  2. Strip comments (single-line, multi-line, docstrings)
  3. Normalize whitespace (collapse runs → single space, trim lines)
  4. Compare:
     a. SHA256 hash match → score 1.0 (perfect Type-1)
     b. SequenceMatcher ratio ≥ 0.98 → near-exact Type-1
        (accounts for minor trailing whitespace differences
         that normalization may not catch)
     c. ratio < 0.98 → NOT Type-1

Threshold justification:
  Type-1 is strictly "same code, different formatting."
  A 0.95 threshold (old code) let through renamed-variable
  pairs because SequenceMatcher on character sequences can
  report 0.95 when only a few short identifiers differ.
  0.98 is tight enough to ensure only whitespace/comment
  differences produce a match.
"""

import difflib
import hashlib
import re
from pathlib import Path
from typing import Any, Dict


class Type1Detector:
    """
    Detects exact clones (whitespace/comment-only differences).

    Score 1.0  = hash-identical after normalization
    Score ≥ 0.98 = near-exact (Type-1 clone)
    Score < 0.98 = NOT a Type-1 clone
    """

    # ── Normalization ─────────────────────────────────────────────────────

    @staticmethod
    def _strip_comments(code: str, language: str = "auto") -> str:
        """
        Remove comments while preserving all actual code.

        Handles:
          - C/C++/Java/JS: // single-line, /* multi-line */
          - Python: # single-line, triple-quote docstrings
          - Preprocessor directives (#include, #define): PRESERVED
            because they are code, not comments
        """
        # Step 1: Remove multi-line comments  /* ... */
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

        # Step 2: Remove Python triple-quote docstrings
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)

        # Step 3: Remove single-line comments
        #   // ... (C-style)
        code = re.sub(r'//[^\n]*', '', code)

        #   # ... (Python-style) — but NOT #include, #define, #pragma, etc.
        #   We only strip '#' when it's NOT followed by a C preprocessor keyword.
        code = re.sub(
            r'#(?!include|define|pragma|ifndef|ifdef|endif|if|else|elif|undef|error|warning|line)\s*[^\n]*',
            '',
            code
        )

        return code

    @staticmethod
    def _normalize_whitespace(code: str) -> str:
        """
        Normalize whitespace without changing any tokens or their case.

        - Collapse runs of whitespace (spaces, tabs, newlines) to single space
        - Strip leading/trailing whitespace
        - Do NOT lowercase (case change = Type-2, not Type-1)
        """
        return re.sub(r'\s+', ' ', code).strip()

    def _normalize(self, code: str) -> str:
        """Full normalization pipeline for Type-1 comparison."""
        code = self._strip_comments(code)
        code = self._normalize_whitespace(code)
        return code

    # ── Detection ─────────────────────────────────────────────────────────

    def detect(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """
        Compare two files for Type-1 (exact) clones.

        Returns:
            {
                "type1_score":  float,   # 0.0 – 1.0
                "is_clone":     bool,    # True if score ≥ 0.98
                "confidence":   str,     # EXACT / HIGH / MEDIUM / LOW / UNLIKELY / ERROR / EMPTY
                "method":       str,     # "hash" or "sequence"
            }
        """
        try:
            code_a = Path(file_a).read_text(encoding='utf-8', errors='ignore')
            code_b = Path(file_b).read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {
                "type1_score": 0.0, "is_clone": False,
                "confidence": "ERROR", "error": str(e), "method": "none",
            }

        norm_a = self._normalize(code_a)
        norm_b = self._normalize(code_b)

        if not norm_a or not norm_b:
            return {
                "type1_score": 0.0, "is_clone": False,
                "confidence": "EMPTY", "method": "none",
            }

        # ── Fast path: exact hash match ───────────────────────────────────
        hash_a = hashlib.sha256(norm_a.encode('utf-8')).hexdigest()
        hash_b = hashlib.sha256(norm_b.encode('utf-8')).hexdigest()

        if hash_a == hash_b:
            return {
                "type1_score": 1.0, "is_clone": True,
                "confidence": "EXACT", "method": "hash",
            }

        # ── Slow path: sequence similarity for near-exact matches ─────────
        #    (catches minor differences that hash can't tolerate,
        #     e.g., trailing semicolon on last line vs not)
        ratio = round(
            difflib.SequenceMatcher(None, norm_a, norm_b).ratio(), 4
        )

        is_clone = ratio >= 0.98

        if ratio >= 0.99:
            confidence = "HIGH"
        elif ratio >= 0.98:
            confidence = "MEDIUM"
        elif ratio >= 0.90:
            confidence = "LOW"
        else:
            confidence = "UNLIKELY"

        return {
            "type1_score": ratio,
            "is_clone":    is_clone,
            "confidence":  confidence,
            "method":      "sequence",
        }