# detectors/type3/fragment_comparator.py
"""
Fragment Comparator — Multi-Tier Clone Type Discrimination
===========================================================

Improvement over previous version:
  - Added MT3 tier (50–70% normalized similarity) per BigCloneBench taxonomy
  - Added clone_band field (VST3 / ST3 / MT3) aligned with Walker et al. 2019
  - Added confidence penalty for MT3 to reduce false positives
  - Added gap_ratio diagnostic (norm_sim - raw_sim)

Clone bands (BigCloneBench taxonomy, Walker et al. 2019):
  VST3: 90–100% normalized similarity (very strongly similar)
  ST3:  70–90%  normalized similarity (strongly similar)
  MT3:  50–70%  normalized similarity (moderately similar)  ← NEW
  WT3:  0–50%   (weakly similar — not detected; too noisy for edu context)

Three-level classification cascade:
  raw ≥ 0.95                          → type1 (exact copy)
  norm ≥ 0.95  AND raw < 0.95         → type2 (renamed identifiers)
  norm ≥ 0.70  AND norm < 0.95        → type3 ST3/VST3 (high confidence)
  norm ≥ 0.50  AND norm < 0.70        → type3 MT3 (medium confidence)
                 AND gap_ratio ≥ 0.08  (ensures renaming or structural change
                                        caused the similarity gap, not just
                                        unrelated similar-length code)
  else                                → none

Research basis:
  Roy & Cordy (2008) — NiCad near-miss clone detection via LCS on normalized tokens
  Walker et al. (2019) — BigCloneBench taxonomy and recall analysis
  Ain et al. (2019) — Systematic review, hybrid approaches outperform single-technique
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from detectors.type3.fragment_extractor import Fragment
from detectors.type3.normalizer import normalize_tokens, structurally_normalize_tokens
from detectors.type3.lcs_comparator import lcs_similarity


# ─── Thresholds ───────────────────────────────────────────────────────────────

TYPE1_RAW_THRESHOLD  = 0.95   # raw ≥ this → exact copy (Type-1)
TYPE2_NORM_THRESHOLD = 0.95   # norm ≥ this → renamed identifiers (Type-2)
TYPE3_ST_THRESHOLD   = 0.70   # norm ≥ this → ST3 / VST3 (Type-3, high confidence)
TYPE3_MT_THRESHOLD   = 0.50   # norm ≥ this → MT3 (Type-3, medium confidence)
MT3_GAP_MIN          = 0.08   # minimum gap_ratio required to confirm MT3
                               # (filters out unrelated code that happens to
                               #  score 50–70% due to similar structure patterns)

# Confidence penalty for MT3: the score is discounted to reflect lower certainty
MT3_SCORE_PENALTY    = 0.85


@dataclass
class FragmentComparisonResult:
    """
    Result of comparing two code fragments using the multi-tier approach.

    Fields:
        raw_similarity:   LCS on original tokens (Type-1 check)
        norm_similarity:  LCS on blind-normalized tokens (Type-2/3 check)
        deep_similarity:  LCS on structurally-normalized tokens (MT3 confirmation)
        gap_ratio:        norm_similarity - raw_similarity (diagnostic)
        clone_type:       "type1" | "type2" | "type3" | "none"
        clone_band:       "VST3" | "ST3" | "MT3" | "type1" | "type2" | "none"
                          VST3 = 90–100% norm sim (very strongly similar Type-3)
                          ST3  = 70–90%  norm sim (strongly similar Type-3)
                          MT3  = 50–70%  norm sim (moderately similar Type-3)
        is_type3:         True only if a genuine Type-3 clone
        type3_score:      The score to report (norm_sim with MT3 penalty if applicable)
        confidence:       "HIGH" | "MEDIUM" | "LOW"
    """
    raw_similarity:  float
    norm_similarity: float
    deep_similarity: float
    gap_ratio:       float
    clone_type:      str
    clone_band:      str
    is_type3:        bool
    type3_score:     float
    confidence:      str


def compare_fragments(frag_a: Fragment, frag_b: Fragment) -> FragmentComparisonResult:
    """
    Compare two code fragments using the multi-tier dual-similarity approach.

    Computes three similarity levels:
      1. raw_sim   — original tokens (detects Type-1: exact copies)
      2. norm_sim  — blind-normalized tokens (detects Type-2: renames, Type-3: structural)
      3. deep_sim  — structurally-normalized (used for MT3 confirmation)
    """
    raw_tokens_a  = frag_a.tokens
    raw_tokens_b  = frag_b.tokens
    norm_tokens_a = normalize_tokens(raw_tokens_a)
    norm_tokens_b = normalize_tokens(raw_tokens_b)
    deep_tokens_a = structurally_normalize_tokens(norm_tokens_a)
    deep_tokens_b = structurally_normalize_tokens(norm_tokens_b)

    raw_sim   = lcs_similarity(raw_tokens_a,  raw_tokens_b)
    norm_sim  = lcs_similarity(norm_tokens_a, norm_tokens_b)
    deep_sim  = lcs_similarity(deep_tokens_a, deep_tokens_b)
    gap_ratio = round(norm_sim - raw_sim, 4)

    clone_type, clone_band, is_type3, type3_score, confidence = _classify(
        raw_sim, norm_sim, deep_sim, gap_ratio
    )

    return FragmentComparisonResult(
        raw_similarity  = raw_sim,
        norm_similarity = norm_sim,
        deep_similarity = deep_sim,
        gap_ratio       = gap_ratio,
        clone_type      = clone_type,
        clone_band      = clone_band,
        is_type3        = is_type3,
        type3_score     = type3_score,
        confidence      = confidence,
    )


def _classify(
    raw_sim:   float,
    norm_sim:  float,
    deep_sim:  float,
    gap_ratio: float,
) -> Tuple[str, str, bool, float, str]:
    """
    Classify a fragment pair.
    Returns: (clone_type, clone_band, is_type3, type3_score, confidence)
    """

    # ── Type-1: exact copy (raw tokens nearly identical) ──────────────────
    if raw_sim >= TYPE1_RAW_THRESHOLD:
        return ("type1", "type1", False, 0.0, "HIGH")

    # ── Type-2: renamed identifiers (norm identical but raw differs) ───────
    if norm_sim >= TYPE2_NORM_THRESHOLD:
        return ("type2", "type2", False, 0.0, "HIGH")

    # ── Type-3 ST3/VST3: strongly similar structural clone ─────────────────
    # norm ≥ 0.70: real structural modifications beyond renaming.
    # Band is VST3 if norm ≥ 0.90, else ST3.
    if norm_sim >= TYPE3_ST_THRESHOLD:
        band       = "VST3" if norm_sim >= 0.90 else "ST3"
        score      = round(norm_sim, 4)
        confidence = "HIGH" if norm_sim >= 0.80 else "MEDIUM"
        return ("type3", band, True, score, confidence)

    # ── Type-3 MT3: moderately similar structural clone ────────────────────
    # norm 0.50–0.70: weaker structural overlap.
    # Requires gap_ratio >= MT3_GAP_MIN to confirm it's not just two
    # unrelated files that happen to use similar control-flow patterns.
    # Also uses deep_sim (structural normalization) as a confirmation signal:
    # if deep_sim is high, the structural skeleton is truly similar.
    if norm_sim >= TYPE3_MT_THRESHOLD:
        # Confirm: either the gap_ratio suggests renaming happened,
        # or the deep structural similarity is high (same skeleton)
        gap_confirms  = gap_ratio >= MT3_GAP_MIN
        deep_confirms = deep_sim >= 0.65

        if gap_confirms or deep_confirms:
            # Apply score penalty to reflect lower certainty
            score = round(norm_sim * MT3_SCORE_PENALTY, 4)
            return ("type3", "MT3", True, score, "LOW")

    return ("none", "none", False, 0.0, "UNLIKELY")


def compare_fragments_raw_only(frag_a: Fragment, frag_b: Fragment) -> float:
    """Quick raw-only comparison (no normalization)."""
    return lcs_similarity(frag_a.tokens, frag_b.tokens)
