# utils/metrics_calculator.py
"""
Metrics Calculator — Expanded Feature Set for Type-3 Detection
==============================================================

Improvements over the previous version:
  1. Added nesting_depth (max control-flow nesting)
  2. Added param_count (total function parameters)
  3. Added return_points (number of return statements)
  4. Added operator_density (operators per LOC)
  5. Added unique_operators (distinct operator types)

The old version only used [LOC, cyclomatic_complexity, function_count].
These three alone miss cases where:
  - Two files have the same LOC/complexity but very different nesting structures
  - One file has deeply nested code while the other is flat (same cyclomatic)
  - Parameter counts differ due to added helper parameters

The expanded 8-feature vector is more discriminating and aligns with
the metric-based detection approaches reviewed in Ain et al. (2019),
specifically the "software metrics" category that uses Euclidean distance
on code quality metrics.

Feature vector: [nloc, cyclomatic, func_count, max_nesting,
                 param_count, return_points, operator_density, unique_ops]
"""

import re
import lizard
import numpy as np
from pathlib import Path
from typing import List


# ─── Operator patterns ────────────────────────────────────────────────────────
_OPERATORS = re.compile(
    r'[+\-*/%]|==|!=|<=|>=|&&|\|\||[!<>&|^~]|<<|>>|\+\+|--|[+\-*/%&|^]=|\?'
)
_RETURN_RE = re.compile(r'\breturn\b')
_NESTING_KEYWORDS = re.compile(
    r'\b(if|else|for|while|do|switch|case|try|catch|except|with)\b'
)


class MetricsCalculator:

    def calculate_file_metrics(self, file_path: str) -> List[float]:
        """
        Compute the expanded 8-feature metric vector for one file.

        Returns:
          [nloc, cyclomatic_complexity, function_count,
           max_nesting_depth, total_param_count,
           return_points, operator_density, unique_operator_count]
        """
        try:
            path_str = str(file_path)
            analysis = lizard.analyze_file(path_str)

            # ── Primary lizard metrics ────────────────────────────────
            nloc           = float(analysis.nloc or 0)
            func_count     = float(len(analysis.function_list))
            total_cyclo    = sum(f.cyclomatic_complexity for f in analysis.function_list)
            # script-style files (no functions): use 1 as baseline complexity
            if func_count == 0 and nloc > 0:
                total_cyclo = 1

            # ── Parameter count ───────────────────────────────────────
            total_params = float(sum(
                len(f.parameters) for f in analysis.function_list
            ))

            # ── Max nesting depth ────────────────────────────────────
            max_nesting = float(max(
                (f.max_nesting_depth for f in analysis.function_list
                 if hasattr(f, "max_nesting_depth")),
                default=0
            ))

            # ── Source-level features (need raw source) ───────────────
            try:
                source = Path(path_str).read_text(encoding="utf-8", errors="ignore")
                return_points   = float(len(_RETURN_RE.findall(source)))
                all_ops         = _OPERATORS.findall(source)
                operator_count  = float(len(all_ops))
                unique_ops      = float(len(set(all_ops)))
                operator_density = round(operator_count / max(nloc, 1), 4)
            except Exception:
                return_points    = 0.0
                operator_density = 0.0
                unique_ops       = 0.0

            return [
                nloc,
                float(total_cyclo),
                func_count,
                max_nesting,
                total_params,
                return_points,
                operator_density,
                unique_ops,
            ]

        except Exception as e:
            print(f"[Metrics] Error for {file_path}: {e}")
            return [0.0] * 8

    def calculate_similarity(self, metrics_a: List[float], metrics_b: List[float]) -> float:
        """
        Compute similarity between two metric vectors.

        Uses a weighted Euclidean distance where features are individually
        normalized by their expected range, so that no single large-valued
        feature (e.g., LOC in hundreds) dominates the distance calculation.

        Weights reflect discriminative power for Type-3 clone detection:
          - cyclomatic complexity: highest weight (algorithm structure)
          - max nesting depth:     high weight (structural shape)
          - operator density:      medium weight
          - LOC, func_count:       lower weight (size-only signals)
          - param_count, returns:  lower weight
          - unique_ops:            lower weight

        Returns a similarity in [0, 1] where 1 = identical metrics.
        """
        a = np.array(metrics_a, dtype=np.float64)
        b = np.array(metrics_b, dtype=np.float64)

        # Per-feature normalization ranges (approximate max values in student code)
        # Prevents large-magnitude features from dominating
        RANGES = np.array([
            200.0,   # nloc
            50.0,    # cyclomatic complexity
            20.0,    # function count
            10.0,    # max nesting depth
            30.0,    # total param count
            30.0,    # return points
            3.0,     # operator density
            30.0,    # unique operators
        ], dtype=np.float64)

        # Feature weights (importance for Type-3 discrimination)
        WEIGHTS = np.array([
            0.10,   # nloc
            0.25,   # cyclomatic complexity  ← most discriminative
            0.10,   # function count
            0.20,   # max nesting depth      ← second most discriminative
            0.10,   # total params
            0.10,   # return points
            0.10,   # operator density
            0.05,   # unique operators
        ], dtype=np.float64)

        # Normalise each feature to [0,1]
        a_norm = np.clip(a / RANGES, 0, 1)
        b_norm = np.clip(b / RANGES, 0, 1)

        # Weighted Euclidean distance, scaled to [0, 1]
        diff        = (a_norm - b_norm) * WEIGHTS
        weighted_dist = float(np.sqrt(np.sum(diff ** 2)))
        max_dist      = float(np.sqrt(np.sum(WEIGHTS ** 2)))  # max possible distance

        # Similarity = 1 - normalized_distance
        similarity = 1.0 - (weighted_dist / max(max_dist, 1e-9))
        return round(float(np.clip(similarity, 0.0, 1.0)), 4)

    def feature_names(self) -> List[str]:
        """Return the names of the 8 features, for CSV export."""
        return [
            "loc", "cyclomatic_complexity", "function_count",
            "max_nesting_depth", "param_count", "return_points",
            "operator_density", "unique_operators",
        ]
