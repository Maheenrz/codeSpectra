# detectors/type3/normalizer.py
"""
Token Normalizer — Blind Identifier Renaming
==============================================
Applies blind normalization to token sequences:

  - All identifiers (non-keywords) → VAR_0, VAR_1, ...
    (same identifier gets the same VAR_N within one fragment)
  - String literals   → STR
  - Numeric literals  → NUM
  - Comments are already stripped by FragmentExtractor

Why this matters for clone detection:
  After normalization, two fragments that differ ONLY in variable names
  become IDENTICAL. This is the key insight:

  - If raw tokens are identical          → Type-1 clone (exact copy)
  - If raw tokens differ but normalized
    tokens are identical                  → Type-2 clone (renamed variables)
  - If even normalized tokens differ
    but are still highly similar          → Type-3 clone (structural modification)

  The old code only computed normalized similarity and called everything
  "Type-3". The new approach compares BOTH raw and normalized to correctly
  discriminate between clone types.
"""

from __future__ import annotations
import re
from typing import List, Dict

# ── Keywords: never renamed during normalization ──────────────────────────────
# These are language-reserved words and operators that carry structural
# meaning. Renaming them would destroy the code's semantics.

_KEYWORDS = {
    # C / C++
    "if","else","for","while","do","switch","case","break","continue","return",
    "void","int","float","double","char","bool","long","short","unsigned","signed",
    "const","static","inline","virtual","public","private","protected","class",
    "struct","namespace","template","typename","new","delete","try","catch","throw",
    "true","false","nullptr","NULL","sizeof","typedef","using","auto",
    # Java
    "extends","implements","interface","abstract","final","this","super","import",
    "package","throws","instanceof","synchronized","volatile","transient","native",
    "boolean","byte","String","System","println",
    # Python
    "def","lambda","import","from","as","with","yield","async","await","pass",
    "global","nonlocal","not","and","or","in","is","None","True","False",
    "print","len","range","enumerate","zip","map","filter","list","dict","set",
    "tuple","str","int","float","bool","type","isinstance","hasattr","getattr",
    # JavaScript
    "function","var","let","const","=>","typeof","instanceof","void","delete",
    "in","of","yield","async","await","export","default","from","import","require",
    # Operators / punctuation kept as-is
    "{","}","(",")",";",",","[","]",".",":","=","+","-","*","/","%",
    "==","!=","<",">","<=",">=","&&","||","!","&","|","^","~","<<",">>",
    "++","--","+=","-=","*=","/=","->","::","?",
}

_STRING_RE  = re.compile(r'"[^"]*"|\'[^\']*\'')
_NUMBER_RE  = re.compile(r'\b\d+(?:\.\d+)?\b')
_IDENT_RE   = re.compile(r'\b[a-zA-Z_]\w*\b')


def normalize_tokens(tokens: List[str]) -> List[str]:
    """
    Apply blind normalization to a token list.

    Each unique non-keyword identifier gets mapped to VAR_0, VAR_1, etc.
    String literals → STR, numeric literals → NUM.
    Keywords and operators pass through unchanged.

    Returns a new list of normalized tokens.
    """
    id_map: Dict[str, str] = {}
    counter = [0]  # use list for closure mutation

    def _map_id(name: str) -> str:
        if name in _KEYWORDS:
            return name
        if name not in id_map:
            id_map[name] = f"VAR_{counter[0]}"
            counter[0] += 1
        return id_map[name]

    normalized = []
    for tok in tokens:
        if _STRING_RE.fullmatch(tok):
            normalized.append("STR")
        elif _NUMBER_RE.fullmatch(tok):
            normalized.append("NUM")
        elif _IDENT_RE.fullmatch(tok):
            normalized.append(_map_id(tok))
        else:
            normalized.append(tok)

    return normalized