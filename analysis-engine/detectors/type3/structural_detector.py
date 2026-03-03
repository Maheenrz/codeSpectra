# detectors/type3/structural_detector.py
"""
Structural Type-3 Clone Detector
==================================
Fragment-level Type-3 detector that correctly discriminates between
clone types using dual-similarity comparison.

Pipeline:
  Step 1 — Fragment extraction     (FragmentExtractor)
  Step 2 — Dual-similarity compare (FragmentComparator)
            Computes raw + normalized LCS for every fragment pair.
            Filters OUT Type-1 and Type-2 matches.
  Step 3 — Clone clustering        (CloneClusterer)

Key difference from the old approach:
  The old detector normalized all tokens and ran LCS on normalized
  sequences only. This meant Type-2 clones (just renamed variables)
  scored ~100% and got misreported as Type-3.

  This detector computes BOTH raw and normalized similarity. If the
  gap between them shows that normalization made the fragments
  identical → that's Type-2, not Type-3. We only report genuine
  structural modifications as Type-3.

Public API:
  detect(file_a, file_b)    → best Type-3 score between two files
  detect_batch(file_paths)  → full batch with clone clustering
  get_diff_blocks(a, b)     → matching token blocks for frontend diff
"""

from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from detectors.type3.fragment_extractor import FragmentExtractor, Fragment
from detectors.type3.fragment_comparator import (
    compare_fragments,
    FragmentComparisonResult,
    TYPE3_NORM_THRESHOLD,
)
from detectors.type3.normalizer import normalize_tokens
from detectors.type3.lcs_comparator import lcs_similarity, get_matching_blocks
from detectors.type3.clone_clusterer import CloneClusterer


class StructuralDetector:
    """
    Fragment-level Type-3 detector.
    Operates at fragment (function/method/block) granularity,
    not at whole-file granularity.

    Only reports genuine Type-3 clones — Type-1 and Type-2 are
    filtered out by the dual-similarity discriminator.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.70,   # minimum normalized similarity for Type-3
        min_fragment_lines:   int   = 6,
        min_fragment_tokens:  int   = 20,
    ):
        self.threshold     = similarity_threshold
        self.extractor     = FragmentExtractor(
            min_lines  = min_fragment_lines,
            min_tokens = min_fragment_tokens,
        )
        self.clusterer     = CloneClusterer()
        self._frag_cache:  Dict[str, List[Fragment]] = {}  # file_path → fragments

    # ── Public API ────────────────────────────────────────────────────────────

    def prepare_batch(self, file_paths: List[str]) -> None:
        """
        Pre-extract all fragments for a batch.
        Call this once before running detect() on many pairs.
        """
        for fp in file_paths:
            self._get_fragments(fp)

    def detect(
        self,
        file_a: str,
        file_b: str,
    ) -> Dict:
        """
        Compare two files at fragment level.

        Returns the best TYPE-3 ONLY fragment-pair similarity.
        Type-1 and Type-2 matches are detected but filtered out.

        Return dict:
        {
            "type3_score":      float,  # best Type-3 score (0.0 if none found)
            "is_clone":         bool,   # True if a Type-3 clone was found
            "clone_pairs":      [...],  # all Type-3 fragment pairs
            "discrimination": {         # what was filtered out
                "type1_pairs":  int,
                "type2_pairs":  int,
                "type3_pairs":  int,
                "none_pairs":   int,
            },
            "best_raw_sim":     float,  # highest raw similarity seen
            "best_norm_sim":    float,  # highest normalized similarity seen
            "frag_count_a":     int,
            "frag_count_b":     int,
        }
        """
        frags_a = self._get_fragments(file_a)
        frags_b = self._get_fragments(file_b)

        if not frags_a or not frags_b:
            return {
                "type3_score":    0.0,
                "is_clone":       False,
                "clone_pairs":    [],
                "discrimination": {"type1_pairs": 0, "type2_pairs": 0,
                                   "type3_pairs": 0, "none_pairs": 0},
                "best_raw_sim":   0.0,
                "best_norm_sim":  0.0,
                "frag_count_a":   0,
                "frag_count_b":   0,
            }

        best_type3_score = 0.0
        best_raw_sim     = 0.0
        best_norm_sim    = 0.0
        type3_pairs: List[Dict] = []
        counts = {"type1_pairs": 0, "type2_pairs": 0,
                  "type3_pairs": 0, "none_pairs": 0}

        for fa in frags_a:
            for fb in frags_b:
                result = compare_fragments(fa, fb)

                # Track the highest similarities seen (for debugging/logging)
                if result.raw_similarity > best_raw_sim:
                    best_raw_sim = result.raw_similarity
                if result.norm_similarity > best_norm_sim:
                    best_norm_sim = result.norm_similarity

                # Count by clone type for the discrimination report
                counts[f"{result.clone_type}_pairs"] += 1

                # Only keep genuine Type-3 pairs
                if result.is_type3:
                    type3_pairs.append({
                        "frag_a":          fa,
                        "frag_b":          fb,
                        "similarity":      result.type3_score,
                        "raw_similarity":  result.raw_similarity,
                        "norm_similarity": result.norm_similarity,
                        "clone_type":      result.clone_type,
                    })
                    if result.type3_score > best_type3_score:
                        best_type3_score = result.type3_score

        return {
            "type3_score":    round(best_type3_score, 4),
            "is_clone":       best_type3_score >= self.threshold,
            "clone_pairs":    type3_pairs,
            "discrimination": counts,
            "best_raw_sim":   round(best_raw_sim, 4),
            "best_norm_sim":  round(best_norm_sim, 4),
            "frag_count_a":   len(frags_a),
            "frag_count_b":   len(frags_b),
        }

    def detect_batch(
        self,
        file_paths: List[str],
    ) -> Dict:
        """
        Full batch run: extract → compare all pairs → cluster.
        Used for intra-project / single-zip analysis.
        """
        t0 = time.time()
        self.prepare_batch(file_paths)

        n = len(file_paths)
        all_fragment_pairs: List[Dict] = []
        file_pair_scores:   Dict[Tuple, float] = {}

        for i in range(n):
            frags_i = self._get_fragments(file_paths[i])
            for j in range(i + 1, n):
                frags_j = self._get_fragments(file_paths[j])
                best = 0.0
                for fa in frags_i:
                    for fb in frags_j:
                        result = compare_fragments(fa, fb)
                        # Only cluster genuine Type-3 pairs
                        if result.is_type3:
                            all_fragment_pairs.append({
                                "frag_a":     fa,
                                "frag_b":     fb,
                                "similarity": result.type3_score,
                            })
                            if result.type3_score > best:
                                best = result.type3_score
                file_pair_scores[(i, j)] = best

        clone_classes = self.clusterer.cluster(
            all_fragment_pairs, min_similarity=self.threshold
        )

        return {
            "file_pair_scores":  file_pair_scores,
            "clone_classes":     [c.to_dict() for c in clone_classes],
            "total_fragments":   sum(
                len(self._get_fragments(fp)) for fp in file_paths
            ),
            "total_clone_pairs": len(all_fragment_pairs),
            "processing_ms":     round((time.time() - t0) * 1000, 1),
        }

    def get_diff_blocks(self, file_a: str, file_b: str) -> List[Dict]:
        """
        Return matching token blocks for the best Type-3 fragment pair.
        Used by the frontend diff/highlight view.
        """
        result = self.detect(file_a, file_b)
        if not result["clone_pairs"]:
            return []
        best_pair = max(result["clone_pairs"], key=lambda p: p["similarity"])
        fa = best_pair["frag_a"]
        fb = best_pair["frag_b"]
        norm_a = normalize_tokens(fa.tokens)
        norm_b = normalize_tokens(fb.tokens)
        blocks = get_matching_blocks(norm_a, norm_b)
        return [
            {"i": i, "j": j, "n": n}
            for i, j, n in blocks if n > 0
        ]

    def clear_cache(self) -> None:
        self._frag_cache.clear()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_fragments(self, file_path: str) -> List[Fragment]:
        if file_path not in self._frag_cache:
            self._frag_cache[file_path] = self.extractor.extract(file_path)
        return self._frag_cache[file_path]