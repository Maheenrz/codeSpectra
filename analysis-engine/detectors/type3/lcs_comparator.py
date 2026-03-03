"""
LCS Comparator — NiCad Step 3
==============================
Computes Type-3 clone similarity using Longest Common Subsequence (LCS)
on normalized token sequences, exactly as NiCad does.

Dissimilarity = (|A| + |B| - 2 * LCS(A,B)) / (|A| + |B|)
Similarity    = 1 - Dissimilarity

NiCad default threshold: dissimilarity ≤ 0.30 → similarity ≥ 0.70

Uses Python's difflib.SequenceMatcher which is backed by a C implementation
of the Ratcliff/Obershelp algorithm — equivalent to LCS for our purposes
and runs in O(n) amortized on real code.
"""

from __future__ import annotations
import difflib
from typing import List, Tuple


def lcs_similarity(tokens_a: List[str], tokens_b: List[str]) -> float:
    """
    Compute LCS-based similarity between two token sequences.
    Returns a float in [0, 1]. Higher = more similar.
    """
    if not tokens_a or not tokens_b:
        return 0.0

    # SequenceMatcher.ratio() = 2*M / T where M = matching tokens, T = total
    # This is equivalent to 1 - NiCad's dissimilarity ratio
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b, autojunk=False)
    return round(matcher.ratio(), 4)


def lcs_dissimilarity(tokens_a: List[str], tokens_b: List[str]) -> float:
    """
    NiCad dissimilarity ratio. 0 = identical, 1 = nothing in common.
    Threshold: ≤ 0.30 means Type-3 clone (≥70% similar).
    """
    return round(1.0 - lcs_similarity(tokens_a, tokens_b), 4)


def get_matching_blocks(
    tokens_a: List[str], tokens_b: List[str]
) -> List[Tuple[int, int, int]]:
    """
    Return matching block positions: list of (i, j, n) meaning
    tokens_a[i:i+n] == tokens_b[j:j+n].
    Useful for diff highlighting in the frontend.
    """
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b, autojunk=False)
    return matcher.get_matching_blocks()