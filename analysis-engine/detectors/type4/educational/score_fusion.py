# detectors/type4/educational/score_fusion.py
"""
Score Fusion — combines PDG, I/O behavioral, and algorithm signature signals.

This is the decision layer for Type-4 educational clone detection.

Fusion formula (when I/O is available):
  final = pdg_score × 0.35
        + io_match   × 0.45
        + algo_sig   × 0.20

When I/O is unavailable (execution failed):
  final = pdg_score × 0.60
        + algo_sig   × 0.40

Algorithm signature scoring:
  same_family  →  1.0   (same algorithm, different implementation)
  unknown      →  0.50  (no classifier result for one/both files)
  different    →  0.20  (different algorithms — reduces Type-4 concern)

Confidence bands (from Walker et al., research recommendation):
  final ≥ 0.80  AND io_match ≥ 0.90  → HIGH (strong plagiarism evidence)
  final ≥ 0.65  AND io_match ≥ 0.70  → MEDIUM
  final ≥ 0.50                        → LOW
  else                                → UNLIKELY

Classification labels for the engine:
  is_semantic_clone = final ≥ threshold (default 0.60)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# ─── Weights ─────────────────────────────────────────────────────────────────

# When I/O behavioral testing succeeded
W_PDG_IO = 0.35
W_IO     = 0.45
W_SIG    = 0.20

# When I/O behavioral testing could not run
W_PDG_NO_IO = 0.60
W_SIG_NO_IO = 0.40

# Default threshold for is_semantic_clone
DEFAULT_THRESHOLD = 0.60

# Algorithm signature score values
SIG_SAME      = 1.00
SIG_UNKNOWN   = 0.50
SIG_DIFFERENT = 0.20


# ─── Input dataclass ─────────────────────────────────────────────────────────

@dataclass
class FusionInput:
    """
    All signals available for score fusion.

    Fields:
        pdg_score         : WL kernel similarity from Joern (0.0–1.0).
                            None if Joern is unavailable.
        io_match_score    : Fraction of test cases with identical outputs (0.0–1.0).
                            None if execution could not be run.
        mutual_correctness: Fraction of cases where BOTH outputs match expected.
                            None if not computed.
        same_algo_family  : True/False/None
                              True  = both files classified as same algorithm family
                              False = different families
                              None  = classifier could not determine
        algorithm_a       : e.g. "BUBBLE_SORT"
        algorithm_b       : e.g. "SELECTION_SORT"
        category          : problem category, e.g. "SORT_ARRAY"
        language          : file language (for threshold adjustment)
    """
    pdg_score:          Optional[float] = None
    io_match_score:     Optional[float] = None
    mutual_correctness: Optional[float] = None
    same_algo_family:   Optional[bool]  = None
    algorithm_a:        str = ""
    algorithm_b:        str = ""
    category:           str = ""
    language:           str = ""


# ─── Output dataclass ────────────────────────────────────────────────────────

@dataclass
class FusionResult:
    """
    Final fused Type-4 score and classification.

    Fields:
        final_score       : 0.0–1.0 combined score used for is_semantic_clone.
        is_semantic_clone : True if final_score ≥ threshold.
        confidence        : "HIGH" | "MEDIUM" | "LOW" | "UNLIKELY"
        threshold_used    : The threshold applied.
        pdg_contribution  : How much the PDG signal contributed.
        io_contribution   : How much the I/O signal contributed.
        sig_contribution  : How much the algorithm signature contributed.
        io_available      : Whether I/O testing ran successfully.
        interpretation    : Human-readable explanation for the result.
        category_scores   : Sub-scores dict for the engine response.
    """
    final_score:          float  = 0.0
    is_semantic_clone:    bool   = False
    confidence:           str    = "UNLIKELY"
    threshold_used:       float  = DEFAULT_THRESHOLD
    pdg_contribution:     float  = 0.0
    io_contribution:      float  = 0.0
    sig_contribution:     float  = 0.0
    io_available:         bool   = False
    interpretation:       str    = ""
    category_scores:      dict   = None

    def __post_init__(self):
        if self.category_scores is None:
            self.category_scores = {}

    def to_detector_dict(self) -> dict:
        """
        Return the dict shape expected by engine/analyzer.py's _run_semantic().
        """
        return {
            "semantic_score":    round(self.final_score, 4),
            "is_semantic_clone": self.is_semantic_clone,
            "confidence":        self.confidence,
            "backend":           "educational_type4",
            "category_scores": {
                "control_flow": round(self.category_scores.get("control_flow", 0.0), 4),
                "data_flow":    round(self.category_scores.get("data_flow",    0.0), 4),
                "call_pattern": round(self.category_scores.get("call_pattern", 0.0), 4),
                "structural":   round(self.category_scores.get("structural",   0.0), 4),
                "behavioral":   round(self.io_contribution, 4),
            },
            "io_match_score":       round(self.io_contribution / (W_IO or 1), 4),
            "io_available":         self.io_available,
            "interpretation":       self.interpretation,
        }


# ─── Fusion function ─────────────────────────────────────────────────────────

def fuse_scores(
    inp:       FusionInput,
    threshold: float = DEFAULT_THRESHOLD,
) -> FusionResult:
    """
    Fuse all available signals into a single Type-4 score.

    Args:
        inp:       All available signals.
        threshold: Score threshold for is_semantic_clone decision.

    Returns:
        FusionResult — always returns a result, never raises.
    """
    logger.debug(
        "[ScoreFusion] pdg=%.3f io=%s algo_same=%s category=%s",
        inp.pdg_score or 0.0,
        f"{inp.io_match_score:.3f}" if inp.io_match_score is not None else "None",
        inp.same_algo_family,
        inp.category,
    )

    result = FusionResult(threshold_used=threshold)

    # ── Signal: algorithm signature ───────────────────────────────────────
    if inp.same_algo_family is True:
        sig_score = SIG_SAME
        sig_label = "same_family"
    elif inp.same_algo_family is False:
        sig_score = SIG_DIFFERENT
        sig_label = "different_family"
    else:
        sig_score = SIG_UNKNOWN
        sig_label = "unknown"

    # ── Signal: PDG WL kernel ─────────────────────────────────────────────
    pdg_score = inp.pdg_score if inp.pdg_score is not None else 0.0

    # ── Fusion ────────────────────────────────────────────────────────────
    io_available = inp.io_match_score is not None

    if io_available:
        io_score = inp.io_match_score  # type: ignore[assignment]

        pdg_contrib = pdg_score * W_PDG_IO
        io_contrib  = io_score  * W_IO
        sig_contrib = sig_score * W_SIG

        final = pdg_contrib + io_contrib + sig_contrib
        result.io_available = True
        result.io_contribution = round(io_contrib, 4)
    else:
        # I/O not available — use PDG + signature only
        pdg_contrib = pdg_score * W_PDG_NO_IO
        sig_contrib = sig_score * W_SIG_NO_IO
        io_contrib  = 0.0

        final = pdg_contrib + sig_contrib
        result.io_available    = False
        result.io_contribution = 0.0

    final = min(max(final, 0.0), 1.0)   # clamp to [0, 1]

    result.final_score       = round(final, 4)
    result.pdg_contribution  = round(pdg_contrib, 4)
    result.sig_contribution  = round(sig_contrib, 4)

    # ── is_semantic_clone decision ────────────────────────────────────────
    result.is_semantic_clone = final >= threshold

    # ── Confidence ───────────────────────────────────────────────────────
    result.confidence = _determine_confidence(
        final=final,
        io_score=inp.io_match_score,
        pdg_score=pdg_score,
        same_algo=inp.same_algo_family,
        io_available=io_available,
    )

    # ── Category scores (mapped to engine interface) ──────────────────────
    # PDG carries control/data flow info; behavioral carries I/O info.
    result.category_scores = {
        "control_flow": pdg_score * 0.5,   # proxy from PDG
        "data_flow":    pdg_score * 0.5,   # proxy from PDG
        "call_pattern": sig_score * 0.5,
        "structural":   pdg_score * 0.4,
        "behavioral":   inp.io_match_score if inp.io_match_score is not None else 0.0,
    }

    # ── Human-readable interpretation ─────────────────────────────────────
    result.interpretation = _build_interpretation(
        inp=inp,
        final=final,
        sig_label=sig_label,
        io_available=io_available,
        confidence=result.confidence,
        is_clone=result.is_semantic_clone,
    )

    logger.info(
        "[ScoreFusion] final=%.3f confidence=%s is_clone=%s  "
        "(pdg=%.3f×%.2f + io=%s×%.2f + sig=%.2f×%.2f)",
        final, result.confidence, result.is_semantic_clone,
        pdg_score, W_PDG_IO if io_available else W_PDG_NO_IO,
        f"{inp.io_match_score:.3f}" if io_available else "N/A",
        W_IO if io_available else 0.0,
        sig_score, W_SIG if io_available else W_SIG_NO_IO,
    )

    return result


def _determine_confidence(
    final:       float,
    io_score:    Optional[float],
    pdg_score:   float,
    same_algo:   Optional[bool],
    io_available: bool,
) -> str:
    """
    Determine confidence level.

    HIGH:     Strong evidence from multiple signals (I/O + PDG + same algo).
    MEDIUM:   I/O matches well or PDG is high, but not all signals agree.
    LOW:      Some signal present but weak.
    UNLIKELY: Below threshold on all signals.
    """
    if io_available and io_score is not None:
        # With I/O testing available
        if io_score >= 0.90 and pdg_score >= 0.55 and same_algo is True and final >= 0.80:
            return "HIGH"
        if io_score >= 0.80 and final >= 0.70:
            return "MEDIUM"
        if io_score >= 0.65 or final >= 0.60:
            return "LOW"
        return "UNLIKELY"
    else:
        # Without I/O testing
        if pdg_score >= 0.75 and same_algo is True and final >= 0.70:
            return "MEDIUM"
        if pdg_score >= 0.60 or final >= 0.55:
            return "LOW"
        return "UNLIKELY"


def _build_interpretation(
    inp:          FusionInput,
    final:        float,
    sig_label:    str,
    io_available: bool,
    confidence:   str,
    is_clone:     bool,
) -> str:
    """Build a plain-English explanation of the result."""
    parts = []

    if inp.category:
        parts.append(f"Problem: {inp.category}")

    if io_available and inp.io_match_score is not None:
        pct = round(inp.io_match_score * 100)
        parts.append(f"I/O match: {pct}%")
    else:
        parts.append("I/O testing: unavailable")

    if inp.pdg_score is not None:
        parts.append(f"PDG similarity: {round(inp.pdg_score * 100)}%")

    if sig_label == "same_family":
        parts.append(
            f"Algorithm: both use {inp.algorithm_a} "
            f"(same family — different implementation)"
        )
    elif sig_label == "different_family":
        parts.append(
            f"Algorithm: A={inp.algorithm_a or '?'} B={inp.algorithm_b or '?'} "
            f"(different algorithms, same output — possible independent correct solutions)"
        )
    else:
        parts.append("Algorithm: classification uncertain")

    verdict = (
        "⚠️ Semantic clone detected" if is_clone
        else "✅ Not a semantic clone"
    )
    parts.append(f"{verdict} (score={round(final * 100)}%, confidence={confidence})")

    return " | ".join(parts)
