# detectors/type3/lcs_comparator.py
"""
LCS-Based Token Sequence Comparator
=====================================
Computes similarity between two token sequences using the
Longest Common Subsequence (LCS) algorithm.

Uses Python's difflib.SequenceMatcher which implements the
Ratcliff/Obershelp algorithm — functionally equivalent to LCS
for our purposes and runs in O(n) amortized on real code.

Formula:
  similarity = 2 * matching_tokens / total_tokens
  This gives a value in [0, 1] where 1.0 = identical sequences.
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

    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b, autojunk=False)
    return round(matcher.ratio(), 4)


def lcs_dissimilarity(tokens_a: List[str], tokens_b: List[str]) -> float:
    """
    Dissimilarity ratio. 0 = identical, 1 = nothing in common.
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