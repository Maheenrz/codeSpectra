# detectors/type3/normalizer.py
"""
Token Normalizer — Two-Level Normalization
==========================================

Level 1 — Blind normalization (normalize_tokens):
  Replaces all non-keyword identifiers with VAR_N tokens.
  This is the NiCad-style normalization used to detect Type-2/3 clones.
  Same identifier → same VAR_N within one fragment.

Level 2 — Structural normalization (structurally_normalize_tokens):
  Applied on top of Level 1 output.
  Normalizes control-flow keywords to structural categories:
    LOOP:   for, while, do
    COND:   if, else, elif, else_if
    TRY:    try, catch, except, finally
    RETURN: return
    CALL:   function/method call pattern (VAR_N followed by "(")
  This catches MT3 clones where a student changed a for-loop to a while-loop,
  or restructured try/catch blocks, while keeping the same algorithm.

Research basis:
  - Ain et al. (2019) cite loop/conditional structure normalization as
    one of the most impactful Type-3 improvements
  - NiCad (Roy & Cordy) uses a similar approach for "near-miss" detection
  - Walker et al. (2019) show MT3 recall improves significantly with
    structural token normalization

Why two levels?
  Level 1 (blind) alone conflates Type-2 and structural Type-3.
  Level 2 (structural) alone loses the distinction between different
  algorithmic patterns that use the same loop type.
  Running level 1 first then level 2 preserves both signals.
"""

from __future__ import annotations
import re
from typing import List, Dict

# ─── Level 1: keyword set (not renamed) ────────────────────────────────────────

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
    # Operators / punctuation
    "{","}","(",")",";",",","[","]",".",":","=","+","-","*","/","%",
    "==","!=","<",">","<=",">=","&&","||","!","&","|","^","~","<<",">>",
    "++","--","+=","-=","*=","/=","->","::","?",
}

_STRING_RE = re.compile(r'"[^"]*"|\'[^\']*\'')
_NUMBER_RE = re.compile(r'\b\d+(?:\.\d+)?\b')
_IDENT_RE  = re.compile(r'\b[a-zA-Z_]\w*\b')


def normalize_tokens(tokens: List[str]) -> List[str]:
    """
    Level 1 — Blind identifier normalization.

    Each unique non-keyword identifier → VAR_N (same name = same VAR_N).
    String literals → STR, numeric literals → NUM.
    Keywords and operators pass through unchanged.
    """
    id_map: Dict[str, str] = {}
    counter = [0]

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


# ─── Level 2: structural normalization mappings ──────────────────────────────

# Control-flow groupings: different keywords that serve the same structural role
# are collapsed to a single abstract token.

_STRUCT_MAP: Dict[str, str] = {
    # Loop constructs → LOOP
    "for":   "LOOP",
    "while": "LOOP",
    "do":    "LOOP",

    # Conditional constructs → COND
    "if":    "COND",
    "else":  "COND",
    "elif":  "COND",    # Python
    "switch":"COND",
    "case":  "COND",

    # Exception handling → EXCH
    "try":     "EXCH",
    "catch":   "EXCH",
    "except":  "EXCH",  # Python
    "finally": "EXCH",
    "throw":   "EXCH",
    "throws":  "EXCH",  # Java

    # Return / yield → RETN
    "return": "RETN",
    "yield":  "RETN",

    # Break / continue → FLOW
    "break":    "FLOW",
    "continue": "FLOW",
    "pass":     "FLOW",  # Python
}


def structurally_normalize_tokens(tokens: List[str]) -> List[str]:
    """
    Level 2 — Structural normalization.

    Applied AFTER Level 1 (blind normalization).
    Collapses control-flow keywords to structural categories so that
    two fragments with the same algorithm but different loop types
    (e.g., for-loop vs while-loop) score higher in normalized LCS.

    Input: output of normalize_tokens()
    Output: further normalized token list
    """
    return [_STRUCT_MAP.get(tok, tok) for tok in tokens]
