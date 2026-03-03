"""
Normalizer — NiCad Step 2
==========================
Applies NiCad-style blind normalization to token sequences:

  - All identifiers (non-keywords) → VAR_0, VAR_1, ...
    (same identifier gets the same VAR_N within one fragment)
  - String literals   → STR
  - Numeric literals  → NUM
  - Comments stripped already by FragmentExtractor

This exposes Type-2 (renamed variable) and Type-3 (near-miss) clones.
Two fragments that differ only in variable names become IDENTICAL after
normalization → LCS similarity = 1.0.
"""

from __future__ import annotations
import re
from typing import List, Dict

# Keywords never renamed
_KEYWORDS = {
    # C / C++
    "if","else","for","while","do","switch","case","break","continue","return",
    "void","int","float","double","char","bool","long","short","unsigned","signed",
    "const","static","inline","virtual","public","private","protected","class",
    "struct","namespace","template","typename","new","delete","try","catch","throw",
    "true","false","nullptr","NULL","sizeof","typedef","using","auto","nullptr",
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
    Apply NiCad-style blind normalization to a token list.
    Returns a new list of normalized tokens.
    """
    # First pass: map each unique identifier to VAR_N
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


def normalize_fragment_tokens(tokens: List[str]) -> List[str]:
    """Convenience wrapper — same as normalize_tokens."""
    return normalize_tokens(tokens)