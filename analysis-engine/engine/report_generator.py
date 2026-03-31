# engine/report_generator.py
"""
CodeSpectra Report Generator -- Dual-Mode CSV Export
====================================================

SUMMARY MODE  (default, human-readable, 8 columns)
  Plain-English column headers sorted by Plagiarism Match % descending.
  Columns:
    Student File 1 | Student File 2 | Plagiarism Match (%) |
    Clone Type | Clone Band | Risk Level |
    Matched Functions | Recommendation

TECHNICAL MODE  (full detail, one row per fragment pair)
  All scores, fragment details, discrimination counts.
  Empty columns auto-dropped.
  Sorted by overall_similarity_pct descending.
  When detailed=True each row represents one compared function pair with:
    function_a_name, function_a_lines, function_b_name, function_b_lines,
    fragment_raw_similarity_pct, fragment_norm_similarity_pct,
    fragment_deep_similarity_pct, fragment_gap_ratio, clone_band
"""

from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


_RECOMMENDATIONS: Dict[tuple, str] = {
    ("type1", "HIGH"):     "Exact duplicate -- flag for immediate review.",
    ("type1", "CRITICAL"): "Exact duplicate -- flag for immediate review.",
    ("type2", "HIGH"):     "Variable renaming detected -- likely deliberate obfuscation.",
    ("type2", "CRITICAL"): "Variable renaming detected -- likely deliberate obfuscation.",
    ("type2", "MEDIUM"):   "Possible identifier renaming -- compare manually.",
    ("type3", "HIGH"):     "Strong structural similarity (ST3/VST3) -- high plagiarism likelihood.",
    ("type3", "CRITICAL"): "Strong structural similarity (VST3) -- immediate review required.",
    ("type3", "MEDIUM"):   "Moderate structural similarity -- review for algorithmic copying.",
    ("type3", "LOW"):      "MT3 clone detected -- similar structure, may be coincidental. Verify.",
}
_REC_DEFAULT = "No significant similarity detected."

_ACTIONS: Dict[str, str] = {
    "CRITICAL": "Flag for immediate instructor review.",
    "HIGH":     "Schedule for review within 24 hours.",
    "MEDIUM":   "Add to review queue.",
    "LOW":      "Monitor -- verify with additional context.",
    "NONE":     "No action required.",
    "UNLIKELY": "No action required.",
}

SUMMARY_COLUMNS = [
    "Student File 1",
    "Student File 2",
    "Plagiarism Match (%)",
    "Clone Type",
    "Clone Band",
    "Risk Level",
    "Matched Functions",
    "Recommendation",
]

TECHNICAL_COLUMNS = [
    "report_id",
    "generated_at",
    "assignment_id",
    "language",
    "file_a_name",
    "file_b_name",
    "primary_clone_type",
    "clone_band",
    "confidence_level",
    "risk_level",
    "overall_similarity_pct",
    "type1_score_pct",
    "type2_score_pct",
    "type3_score_pct",
    "best_fragment_similarity_pct",
    "winnowing_score_pct",
    "ast_structure_score_pct",
    "metrics_score_pct",
    "ml_score_pct",
    "clone_coverage_file_a_pct",
    "clone_coverage_file_b_pct",
    "matched_functions_count",
    "function_a_name",
    "function_a_lines",
    "function_b_name",
    "function_b_lines",
    "fragment_raw_similarity_pct",
    "fragment_norm_similarity_pct",
    "fragment_deep_similarity_pct",
    "fragment_gap_ratio",
    "t1_pairs_filtered",
    "t2_pairs_filtered",
    "strongly_similar_pairs",
    "moderately_similar_pairs",
    "needs_review",
    "recommendation",
    "suggested_action",
    "analysis_notes",
]


def _pct(v: Optional[float]) -> str:
    if v is None:
        return ""
    try:
        return str(round(float(v) * 100, 1))
    except (TypeError, ValueError):
        return ""


def _safe(v: Any, default: str = "") -> str:
    if v is None:
        return default
    return str(v)


def _rec(clone_type: str, confidence: str) -> str:
    return _RECOMMENDATIONS.get(
        (clone_type, confidence),
        _RECOMMENDATIONS.get((clone_type, "MEDIUM"), _REC_DEFAULT),
    )


def _basename(path_str: str) -> str:
    """Return just the filename, stripping any directory components."""
    if not path_str:
        return ""
    return Path(path_str).name or path_str


class ReportGenerator:

    def __init__(self):
        self._ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    def from_analysis_response(
        self,
        response: Dict[str, Any],
        assignment_id: str = "",
        language: str = "",
        mode: str = "summary",
        detailed: bool = True,
    ) -> str:
        pairs = response.get("all_pairs", [])
        pairs = sorted(
            pairs,
            key=lambda p: float(p.get("combined_score") or p.get("structural_score") or 0),
            reverse=True,
        )

        if mode == "summary":
            rows = [self._pair_to_summary_row(p) for p in pairs]
            return self._summary_to_csv(rows)

        # Technical: one row per fragment pair when detailed=True
        all_rows: List[Dict[str, str]] = []
        for p in pairs:
            base  = self._pair_to_technical_row(p, assignment_id, language)
            frags = p.get("fragments", [])

            if detailed and frags:
                base["matched_functions_count"] = str(len(frags))
                for fi, frag in enumerate(frags):
                    row = dict(base)
                    row["report_id"] = str(uuid.uuid4())[:8]

                    # Basename only -- never expose internal upload paths
                    fa_n = _basename(frag.get("file_a", "") or base.get("file_a_name", ""))
                    fb_n = _basename(frag.get("file_b", "") or base.get("file_b_name", ""))

                    frag_sim = frag.get("similarity") or frag.get("norm_similarity") or 0.0

                    row.update({
                        "file_a_name":                  fa_n,
                        "file_b_name":                  fb_n,
                        "overall_similarity_pct":       _pct(frag_sim),
                        "function_a_name":              _safe(frag.get("func_a")),
                        "function_a_lines":             f"L{frag.get('start_a','')}-{frag.get('end_a','')}",
                        "function_b_name":              _safe(frag.get("func_b")),
                        "function_b_lines":             f"L{frag.get('start_b','')}-{frag.get('end_b','')}",
                        "fragment_raw_similarity_pct":  _pct(frag.get("raw_similarity")),
                        "fragment_norm_similarity_pct": _pct(frag.get("norm_similarity")),
                        "fragment_deep_similarity_pct": _pct(frag.get("deep_similarity")),
                        "fragment_gap_ratio":           _safe(frag.get("gap_ratio")),
                        "clone_band":                   frag.get("clone_band", base.get("clone_band", "")),
                        "confidence_level":             frag.get("confidence", base.get("confidence_level", "")),
                        "analysis_notes": (
                            f"Fragment {fi+1}/{len(frags)}: "
                            f"{frag.get('func_a','?')}() vs {frag.get('func_b','?')}() "
                            f"| match={_pct(frag_sim)} "
                            f"raw={_pct(frag.get('raw_similarity'))} "
                            f"norm={_pct(frag.get('norm_similarity'))} "
                            f"band={frag.get('clone_band','')}"
                        ),
                    })
                    all_rows.append(row)
            else:
                all_rows.append(base)

        return self._technical_to_csv(all_rows)

    def from_clone_pairs(
        self,
        clone_pairs: List[Dict[str, Any]],
        assignment_id: str = "",
        language: str = "",
        mode: str = "summary",
    ) -> str:
        pairs = sorted(
            clone_pairs,
            key=lambda p: float(p.get("structural_score") or p.get("effective_score") or 0),
            reverse=True,
        )
        if mode == "summary":
            rows = [self._clone_pair_to_summary_row(p) for p in pairs]
            return self._summary_to_csv(rows)
        rows = [self._clone_pair_to_technical_row(p, assignment_id, language) for p in pairs]
        return self._technical_to_csv(rows)

    # ------------------------------------------------------------------
    # Summary row builders
    # ------------------------------------------------------------------

    def _pair_to_summary_row(self, pair: Dict[str, Any]) -> Dict[str, str]:
        score      = float(pair.get("combined_score") or pair.get("structural_score") or 0)
        clone_type = pair.get("primary_clone_type", "none")
        disc       = pair.get("clone_type_discrimination", {})
        confidence = pair.get("structural", {}).get("confidence", "UNLIKELY")
        sim_level  = pair.get("similarity_level", "NONE")
        frags      = pair.get("fragments", [])
        band       = self._infer_band(clone_type, disc, score)

        # Matched function names
        if frags:
            names = [f"{f.get('func_a','?')}() vs {f.get('func_b','?')}()" for f in frags[:3]]
            matched_fn = " | ".join(names) + (" ..." if len(frags) > 3 else "")
        elif disc.get("type3_pairs_detected", 0):
            matched_fn = f"{disc['type3_pairs_detected']} function pair(s)"
        else:
            matched_fn = ""

        return {
            "Student File 1":       _basename(pair.get("file_a", "")),
            "Student File 2":       _basename(pair.get("file_b", "")),
            "Plagiarism Match (%)": f"{round(score * 100, 1)}%",
            "Clone Type":           self._clone_label(clone_type),
            "Clone Band":           band.upper() if band not in ("none",) else "--",
            "Risk Level":           sim_level,
            "Matched Functions":    matched_fn,
            "Recommendation":       _rec(clone_type, confidence),
        }

    def _clone_pair_to_summary_row(self, cp: Dict[str, Any]) -> Dict[str, str]:
        score      = float(cp.get("structural_score") or cp.get("effective_score") or 0)
        clone_type = cp.get("primary_clone_type", "none")
        confidence = self._score_to_confidence(score)
        sim_level  = cp.get("similarity_level", "NONE")
        return {
            "Student File 1":       _basename(cp.get("file_a", "")),
            "Student File 2":       _basename(cp.get("file_b", "")),
            "Plagiarism Match (%)": f"{round(score * 100, 1)}%",
            "Clone Type":           self._clone_label(clone_type),
            "Clone Band":           self._infer_band(clone_type, {}, score).upper(),
            "Risk Level":           sim_level,
            "Matched Functions":    "",
            "Recommendation":       _rec(clone_type, confidence),
        }

    # ------------------------------------------------------------------
    # Technical row builders
    # ------------------------------------------------------------------

    def _pair_to_technical_row(
        self, pair: Dict[str, Any], assignment_id: str, language: str
    ) -> Dict[str, str]:
        score      = float(pair.get("combined_score") or pair.get("structural_score") or 0)
        clone_type = pair.get("primary_clone_type", "none")
        disc       = pair.get("clone_type_discrimination", {})
        structural = pair.get("structural", {})
        details    = structural.get("details", {})
        confidence = structural.get("confidence", "UNLIKELY")
        sim_level  = pair.get("similarity_level", "NONE")
        band       = self._infer_band(clone_type, disc, score)

        cov_a = details.get("clone_coverage_a", disc.get("clone_coverage_a", 0.0))
        cov_b = details.get("clone_coverage_b", disc.get("clone_coverage_b", 0.0))

        fa_name = _basename(pair.get("file_a", ""))
        fb_name = _basename(pair.get("file_b", ""))

        return {
            "report_id":               str(uuid.uuid4())[:8],
            "generated_at":            self._ts,
            "assignment_id":           _safe(assignment_id),
            "language":                language,
            "file_a_name":             fa_name,
            "file_b_name":             fb_name,
            "primary_clone_type":      clone_type,
            "clone_band":              band,
            "confidence_level":        confidence,
            "risk_level":              sim_level,
            "overall_similarity_pct":  _pct(score),
            "type1_score_pct":         _pct(pair.get("type1_score")),
            "type2_score_pct":         _pct(pair.get("type2_score")),
            "type3_score_pct":         _pct(pair.get("structural_score")),
            "best_fragment_similarity_pct": _pct(details.get("best_fragment_sim")),
            "winnowing_score_pct":     _pct(details.get("winnowing_fingerprint_score")),
            "ast_structure_score_pct": _pct(details.get("ast_skeleton_score")),
            "metrics_score_pct":       _pct(details.get("complexity_metric_score")),
            "ml_score_pct":            _pct(details.get("ml_score")),
            "clone_coverage_file_a_pct": _pct(cov_a),
            "clone_coverage_file_b_pct": _pct(cov_b),
            "matched_functions_count": _safe(disc.get("type3_pairs_detected", 0)),
            "function_a_name":         "",
            "function_a_lines":        "",
            "function_b_name":         "",
            "function_b_lines":        "",
            "fragment_raw_similarity_pct":  "",
            "fragment_norm_similarity_pct": "",
            "fragment_deep_similarity_pct": "",
            "fragment_gap_ratio":      "",
            "t1_pairs_filtered":       _safe(disc.get("type1_pairs_filtered", disc.get("type1_pairs", 0))),
            "t2_pairs_filtered":       _safe(disc.get("type2_pairs_filtered", disc.get("type2_pairs", 0))),
            "strongly_similar_pairs":  _safe(disc.get("vst3_pairs", 0) + disc.get("st3_pairs", 0)),
            "moderately_similar_pairs":_safe(disc.get("mt3_pairs", 0)),
            "needs_review":            "YES" if pair.get("needs_review") else "NO",
            "recommendation":          _rec(clone_type, confidence),
            "suggested_action":        _ACTIONS.get(sim_level, _ACTIONS["NONE"]),
            "analysis_notes":          pair.get("summary", ""),
        }

    def _clone_pair_to_technical_row(
        self, cp: Dict[str, Any], assignment_id: str, language: str
    ) -> Dict[str, str]:
        score      = float(cp.get("structural_score") or cp.get("effective_score") or 0)
        clone_type = cp.get("primary_clone_type", "none")
        confidence = self._score_to_confidence(score)
        sim_level  = cp.get("similarity_level", "NONE")
        band       = self._infer_band(clone_type, {}, score)
        return {
            "report_id":               str(uuid.uuid4())[:8],
            "generated_at":            self._ts,
            "assignment_id":           _safe(assignment_id),
            "language":                language,
            "file_a_name":             _basename(cp.get("file_a", "")),
            "file_b_name":             _basename(cp.get("file_b", "")),
            "primary_clone_type":      clone_type,
            "clone_band":              band,
            "confidence_level":        confidence,
            "risk_level":              sim_level,
            "overall_similarity_pct":  _pct(score),
            "type1_score_pct":         _pct(cp.get("type1_score")),
            "type2_score_pct":         _pct(cp.get("type2_score")),
            "type3_score_pct":         _pct(score),
            "best_fragment_similarity_pct": _pct(score),
            "winnowing_score_pct":     "", "ast_structure_score_pct": "",
            "metrics_score_pct":       "", "ml_score_pct":            "",
            "clone_coverage_file_a_pct": "", "clone_coverage_file_b_pct": "",
            "matched_functions_count": "", "function_a_name": "",
            "function_a_lines": "",       "function_b_name": "",
            "function_b_lines": "",       "fragment_raw_similarity_pct": "",
            "fragment_norm_similarity_pct": "", "fragment_deep_similarity_pct": "",
            "fragment_gap_ratio": "",
            "t1_pairs_filtered":        "", "t2_pairs_filtered": "",
            "strongly_similar_pairs":   "", "moderately_similar_pairs": "",
            "needs_review":            "YES" if cp.get("needs_review") else "NO",
            "recommendation":          _rec(clone_type, confidence),
            "suggested_action":        _ACTIONS.get(sim_level, _ACTIONS["NONE"]),
            "analysis_notes":          cp.get("summary", ""),
        }

    # ------------------------------------------------------------------
    # CSV serialization
    # ------------------------------------------------------------------

    @staticmethod
    def _summary_to_csv(rows: List[Dict[str, str]]) -> str:
        buf = io.StringIO()
        writer = csv.DictWriter(
            buf, fieldnames=SUMMARY_COLUMNS,
            extrasaction="ignore", lineterminator="\n",
        )
        writer.writeheader()
        if rows:
            writer.writerows(rows)
        return buf.getvalue()

    @staticmethod
    def _technical_to_csv(rows: List[Dict[str, str]]) -> str:
        """Write technical CSV, automatically removing entirely-empty columns."""
        if not rows:
            buf = io.StringIO()
            csv.DictWriter(
                buf, fieldnames=TECHNICAL_COLUMNS, lineterminator="\n"
            ).writeheader()
            return buf.getvalue()

        active_cols = [
            col for col in TECHNICAL_COLUMNS
            if any(row.get(col, "") not in ("", None) for row in rows)
        ]

        buf = io.StringIO()
        writer = csv.DictWriter(
            buf, fieldnames=active_cols,
            extrasaction="ignore", lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clone_label(clone_type: str) -> str:
        return {
            "type1": "Type 1 -- Exact Copy",
            "type2": "Type 2 -- Renamed Variables",
            "type3": "Type 3 -- Structural Clone",
            "type4": "Type 4 -- Semantic Clone",
            "none":  "No Clone Detected",
        }.get(clone_type, clone_type)

    @staticmethod
    def _infer_band(clone_type: str, disc: Dict, score: float) -> str:
        if clone_type == "type1":  return "type1"
        if clone_type == "type2":  return "type2"
        if clone_type != "type3":  return "none"
        if disc.get("vst3_pairs", 0): return "VST3"
        if disc.get("st3_pairs",  0): return "ST3"
        if disc.get("mt3_pairs",  0): return "MT3"
        if score >= 0.90: return "VST3"
        if score >= 0.70: return "ST3"
        if score >= 0.50: return "MT3"
        return "none"

    @staticmethod
    def _score_to_confidence(score: float) -> str:
        if score >= 0.85: return "HIGH"
        if score >= 0.65: return "MEDIUM"
        if score >= 0.45: return "LOW"
        return "UNLIKELY"

    # ------------------------------------------------------------------
    # Backwards-compat shims
    # ------------------------------------------------------------------

    def from_analysis_response_detailed(
        self,
        response: Dict[str, Any],
        assignment_id: str = "",
        language: str = "",
    ) -> str:
        return self.from_analysis_response(
            response,
            assignment_id=assignment_id,
            language=language,
            mode="technical",
            detailed=True,
        )
