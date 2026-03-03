# detectors/type3/fragment_comparator.py
"""
Fragment Comparator — Dual-Similarity Clone Type Discrimination
================================================================

This is the CORE of the corrected Type-3 detection logic.

The Problem (old approach):
  The old code normalized all identifiers (Node→VAR_0, Element→VAR_0)
  and then ran LCS on the normalized tokens. This meant that a Type-2
  clone (same code, just renamed variables) would score ~100% and get
  reported as a "Type-3 structural clone" — which is WRONG.

The Fix (dual-similarity):
  We compute TWO similarity scores for every fragment pair:

  1. raw_similarity   = LCS(original_tokens_A, original_tokens_B)
     → measures how similar the code is AS WRITTEN (with real names)

  2. norm_similarity  = LCS(normalized_tokens_A, normalized_tokens_B)
     → measures how similar the code STRUCTURE is (ignoring names)

  Then we use the GAP between them to classify:

  ┌──────────────────────────────────────────────────────────────────┐
  │  raw ≥ 0.95                                                     │
  │    → Type-1: exact copy (identical tokens)                      │
  │    → NOT our job — belongs to the Type-1 detector               │
  │                                                                  │
  │  norm ≥ 0.95  AND  raw < 0.95                                   │
  │    → Type-2: only variable/function names were changed           │
  │    → NOT our job — belongs to the Type-2 detector               │
  │                                                                  │
  │  0.70 ≤ norm < 0.95                                              │
  │    → Type-3: real structural modification beyond just renaming   │
  │    → THIS is what we detect and report ✅                        │
  │                                                                  │
  │  norm < 0.70                                                     │
  │    → Not a structural clone (may still be Type-4 semantic)       │
  │    → NOT our job — belongs to the Type-4 detector               │
  └──────────────────────────────────────────────────────────────────┘

Research basis:
  - Roy & Cordy (2008) define Type-3 as "near-miss clones with
    statement-level modifications" — NOT just renamed variables.
  - The dual-similarity approach is inspired by how tools like
    CCFinder and SourcererCC separate Type-2 from Type-3.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from detectors.type3.fragment_extractor import Fragment
from detectors.type3.normalizer import normalize_tokens
from detectors.type3.lcs_comparator import lcs_similarity


# ── Thresholds for clone type classification ──────────────────────────────────

# If raw similarity is at or above this, it's an exact copy (Type-1)
TYPE1_RAW_THRESHOLD = 0.95

# If normalized similarity is at or above this, the fragments are
# structurally identical (any difference is just renaming → Type-2)
TYPE2_NORM_THRESHOLD = 0.95

# If normalized similarity is at or above this, there is significant
# structural overlap — this is a true Type-3 clone
TYPE3_NORM_THRESHOLD = 0.70


@dataclass
class FragmentComparisonResult:
    """
    Result of comparing two code fragments with dual-similarity.

    Attributes:
        raw_similarity:   LCS score on original (un-normalized) tokens
        norm_similarity:  LCS score on normalized tokens (identifiers → VAR_N)
        clone_type:       "type1", "type2", "type3", or "none"
        is_type3:         True only if this is a genuine Type-3 clone
        type3_score:      The score to report for Type-3 (norm_similarity
                          if type3, else 0.0)
    """
    raw_similarity:  float
    norm_similarity: float
    clone_type:      str     # "type1" | "type2" | "type3" | "none"
    is_type3:        bool
    type3_score:     float   # 0.0 if not type3, else norm_similarity


def compare_fragments(frag_a: Fragment, frag_b: Fragment) -> FragmentComparisonResult:
    """
    Compare two fragments using dual-similarity to determine clone type.

    This is the fundamental operation that fixes the misclassification bug.
    By comparing raw vs normalized similarity, we can tell whether the
    code was just renamed (Type-2) or actually structurally modified (Type-3).
    """
    raw_tokens_a = frag_a.tokens
    raw_tokens_b = frag_b.tokens

    norm_tokens_a = normalize_tokens(raw_tokens_a)
    norm_tokens_b = normalize_tokens(raw_tokens_b)

    # Step 1: Compute both similarity scores
    raw_sim  = lcs_similarity(raw_tokens_a, raw_tokens_b)
    norm_sim = lcs_similarity(norm_tokens_a, norm_tokens_b)

    # Step 2: Classify based on the dual scores
    clone_type, is_type3, type3_score = _classify(raw_sim, norm_sim)

    return FragmentComparisonResult(
        raw_similarity  = raw_sim,
        norm_similarity = norm_sim,
        clone_type      = clone_type,
        is_type3        = is_type3,
        type3_score     = type3_score,
    )


def _classify(
    raw_sim: float,
    norm_sim: float,
) -> tuple:
    """
    Classify a fragment pair based on raw and normalized similarity.

    Returns: (clone_type, is_type3, type3_score)
    """
    # Case 1: Exact copy — raw tokens are nearly identical
    # This is Type-1, not our responsibility
    if raw_sim >= TYPE1_RAW_THRESHOLD:
        return ("type1", False, 0.0)

    # Case 2: After normalization the fragments are nearly identical,
    # but raw tokens differ — the only changes were variable/function names.
    # This is Type-2 (renamed variables), not Type-3.
    if norm_sim >= TYPE2_NORM_THRESHOLD:
        return ("type2", False, 0.0)

    # Case 3: Normalized similarity is high but not perfect —
    # there are real structural changes (added/removed/modified statements).
    # THIS is a genuine Type-3 clone.
    if norm_sim >= TYPE3_NORM_THRESHOLD:
        return ("type3", True, round(norm_sim, 4))

    # Case 4: Not enough structural similarity for Type-3.
    # Could still be a Type-4 semantic clone, but that's not our job.
    return ("none", False, 0.0)


def compare_fragments_raw_only(frag_a: Fragment, frag_b: Fragment) -> float:
    """
    Quick raw-only comparison (no normalization).
    Used when you just need to know if fragments are textually similar.
    """
    return lcs_similarity(frag_a.tokens, frag_b.tokens)