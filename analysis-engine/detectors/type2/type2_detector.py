"""
analysis-engine/detectors/type2/type2_detector.py

Type-2 Clone Detector — Renamed-Identifier Detection
=====================================================

Type-2 clones per Roy & Cordy (2008):
  Structurally identical code fragments except for differences
  in identifier names, literal values, type names, whitespace,
  layout, and comments.

Detection approach:
  1. Tokenize both files (identifiers, keywords, operators, etc.)
  2. Normalize:
     - Language keywords → kept as-is (lowercase)
     - User identifiers  → replaced with 'ID'
     - Numeric literals  → replaced with 'NUM'
     - String literals   → replaced with 'STR'
     - Operators / punctuation → kept as-is
  3. Compare normalized token streams with SequenceMatcher

Threshold justification:
  Type-2 means "structurally identical, only names differ."
  After normalization, a true Type-2 pair should have ratio ≥ 0.90.
  The old threshold of 0.70 was too permissive — it allowed pairs
  with 30% structural differences (added/removed statements) to be
  called Type-2, when they should be Type-3.

  Tiers:
    ratio ≥ 0.90  →  Type-2 clone (HIGH confidence if ≥ 0.95)
    0.80 ≤ ratio < 0.90  →  LOW confidence (borderline)
    ratio < 0.80  →  Not a Type-2 clone
"""

import re
import difflib
from pathlib import Path
from typing import Any, Dict, List


class Type2Detector:
    """
    Type-2 clone detector: detects renamed-variable clones.

    Normalizes identifiers → ID, literals → NUM/STR, then
    compares the normalized token streams.
    """

    KEYWORDS = {
        # C/C++
        'int', 'float', 'double', 'char', 'bool', 'void', 'string', 'auto',
        'long', 'short', 'unsigned', 'signed', 'const', 'static', 'extern',
        'inline', 'virtual', 'override',
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
        'continue', 'return',
        'class', 'struct', 'union', 'enum', 'public', 'private', 'protected',
        'friend', 'new', 'delete', 'nullptr', 'null', 'true', 'false',
        'this', 'operator', 'template', 'namespace', 'using', 'typedef',
        'sizeof', 'dynamic_cast', 'static_cast', 'reinterpret_cast',
        'const_cast', 'try', 'catch', 'throw',
        'cout', 'cin', 'endl', 'printf', 'scanf', 'std', 'vector', 'map',
        'set', 'pair', 'include',
        # Java
        'import', 'package', 'extends', 'implements', 'interface', 'abstract',
        'final', 'throws', 'finally', 'instanceof', 'super',
        # Python
        'def', 'lambda', 'with', 'in', 'is', 'not', 'and', 'or', 'pass',
        'yield', 'from', 'global', 'nonlocal', 'assert', 'raise', 'except',
        'as', 'elif', 'none',
        'print', 'len', 'range', 'list', 'dict', 'tuple', 'str', 'type',
        'self', 'cls',
        # JS/TS
        'function', 'var', 'let', 'typeof', 'async', 'await',
        'export', 'require', 'module', 'console', 'log', 'undefined',
        'of', 'null',
    }

    # ── Tokenization ──────────────────────────────────────────────────────

    def _tokenize(self, code: str) -> List[str]:
        """
        Tokenize code and normalize identifiers/literals.

        Returns a list of normalized tokens where:
          - Keywords stay as-is (lowercase)
          - Identifiers → 'ID'
          - Numbers → 'NUM'
          - String literals → 'STR'
          - Operators / punctuation → kept as-is
        """
        # Strip comments
        code = re.sub(r'//[^\n]*', '', code)
        code = re.sub(r'#(?!include|define|pragma)[^\n]*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)

        # Replace string literals before tokenizing
        code = re.sub(r'"[^"]*"', ' STR ', code)
        code = re.sub(r"'[^']*'", ' STR ', code)

        # Raw token split
        raw = re.findall(
            r'[a-zA-Z_]\w*|'        # identifiers / keywords
            r'\d+\.?\d*|'            # numbers
            r'[+\-*/=<>!&|^%~]+|'   # operators
            r'[(){}\[\];,.]',        # punctuation
            code
        )

        tokens = []
        for tok in raw:
            low = tok.lower()
            if low in self.KEYWORDS:
                tokens.append(low)
            elif re.match(r'^\d', tok):
                tokens.append('NUM')
            elif tok == 'STR':
                tokens.append('STR')
            elif re.match(r'^[a-zA-Z_]', tok):
                tokens.append('ID')
            else:
                tokens.append(tok)
        return tokens

    # ── Detection ─────────────────────────────────────────────────────────

    def detect(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """
        Compare two files for Type-2 (renamed-identifier) clones.

        Returns:
            {
                "type2_score":    float,   # 0.0 – 1.0
                "is_clone":       bool,    # True if score ≥ 0.90
                "confidence":     str,     # HIGH / MEDIUM / LOW / UNLIKELY / ERROR / EMPTY
                "token_count_a":  int,
                "token_count_b":  int,
            }
        """
        try:
            code_a = Path(file_a).read_text(encoding='utf-8', errors='ignore')
            code_b = Path(file_b).read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {
                "type2_score": 0.0, "is_clone": False,
                "confidence": "ERROR", "error": str(e),
            }

        tokens_a = self._tokenize(code_a)
        tokens_b = self._tokenize(code_b)

        if not tokens_a or not tokens_b:
            return {
                "type2_score": 0.0, "is_clone": False,
                "confidence": "EMPTY",
            }

        ratio = round(
            difflib.SequenceMatcher(None, tokens_a, tokens_b).ratio(), 4
        )

        # Type-2 threshold: 0.90
        # After normalizing identifiers → ID and literals → NUM/STR,
        # a true Type-2 pair (same structure, only names differ) should
        # produce ratio ≥ 0.90. Anything lower has real structural changes.
        is_clone = ratio >= 0.90

        if ratio >= 0.95:
            confidence = "HIGH"
        elif ratio >= 0.90:
            confidence = "MEDIUM"
        elif ratio >= 0.80:
            confidence = "LOW"
        else:
            confidence = "UNLIKELY"

        return {
            "type2_score":   ratio,
            "is_clone":      is_clone,
            "confidence":    confidence,
            "token_count_a": len(tokens_a),
            "token_count_b": len(tokens_b),
        }