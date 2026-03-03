"""
NiCad-Style Type-3 Detector
=============================
Implements NiCad's 4-step pipeline without TXL (pure Python):

  Step 1 — Fragment extraction  (FragmentExtractor)
  Step 2 — Normalization        (normalize_tokens)
  Step 3 — LCS comparison       (lcs_similarity)
  Step 4 — Clone clustering     (CloneClusterer)

Compares ALL fragment pairs across ALL files in the batch.
Returns:
  - per-file-pair: best fragment similarity (used by hybrid_detector)
  - clone_classes: grouped clone locations (used by frontend diff view)
"""

from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from detectors.type3.fragment_extractor import FragmentExtractor, Fragment
from detectors.type3.normalizer import normalize_tokens
from detectors.type3.lcs_comparator import lcs_similarity, get_matching_blocks
from detectors.type3.clone_clusterer import CloneClusterer


class NiCadDetector:
    """
    Fragment-level Type-3 detector inspired by NiCad.
    Operates at fragment (function/method/block) granularity,
    not at whole-file granularity.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.70,   # NiCad default: 70%
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
        self._norm_cache:  Dict[str, List[str]]      = {}  # frag_key  → norm tokens

    # ── Public API ────────────────────────────────────────────────────────────

    def prepare_batch(self, file_paths: List[str]) -> None:
        """
        Pre-extract and normalize all fragments for a batch.
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
        Returns the best fragment-pair similarity and all clone pairs found.
        """
        frags_a = self._get_fragments(file_a)
        frags_b = self._get_fragments(file_b)

        if not frags_a or not frags_b:
            return {
                "nicad_score": 0.0,
                "is_clone":    False,
                "clone_pairs": [],
                "frag_count_a": 0,
                "frag_count_b": 0,
            }

        best_sim   = 0.0
        all_pairs: List[Dict] = []

        for fa in frags_a:
            norm_a = self._get_norm(fa)
            for fb in frags_b:
                norm_b = self._get_norm(fb)
                sim    = lcs_similarity(norm_a, norm_b)
                if sim >= self.threshold:
                    all_pairs.append({
                        "frag_a":     fa,
                        "frag_b":     fb,
                        "similarity": sim,
                    })
                if sim > best_sim:
                    best_sim = sim

        return {
            "nicad_score":  round(best_sim, 4),
            "is_clone":     best_sim >= self.threshold,
            "clone_pairs":  all_pairs,
            "frag_count_a": len(frags_a),
            "frag_count_b": len(frags_b),
        }

    def detect_batch(
        self,
        file_paths: List[str],
    ) -> Dict:
        """
        Full NiCad batch run: extract → normalize → compare all pairs → cluster.
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
                    norm_a = self._get_norm(fa)
                    for fb in frags_j:
                        norm_b = self._get_norm(fb)
                        sim    = lcs_similarity(norm_a, norm_b)
                        if sim >= self.threshold:
                            all_fragment_pairs.append({
                                "frag_a":     fa,
                                "frag_b":     fb,
                                "similarity": sim,
                            })
                        if sim > best:
                            best = sim
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
        Return matching token blocks for the best fragment pair.
        Used by the frontend diff/highlight view.
        """
        result = self.detect(file_a, file_b)
        if not result["clone_pairs"]:
            return []
        best_pair = max(result["clone_pairs"], key=lambda p: p["similarity"])
        fa = best_pair["frag_a"]
        fb = best_pair["frag_b"]
        norm_a = self._get_norm(fa)
        norm_b = self._get_norm(fb)
        blocks = get_matching_blocks(norm_a, norm_b)
        return [
            {"i": i, "j": j, "n": n}
            for i, j, n in blocks if n > 0
        ]

    def clear_cache(self) -> None:
        self._frag_cache.clear()
        self._norm_cache.clear()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_fragments(self, file_path: str) -> List[Fragment]:
        if file_path not in self._frag_cache:
            self._frag_cache[file_path] = self.extractor.extract(file_path)
        return self._frag_cache[file_path]

    def _frag_key(self, frag: Fragment) -> str:
        return f"{frag.file_path}::{frag.name}::{frag.start_line}"

    def _get_norm(self, frag: Fragment) -> List[str]:
        key = self._frag_key(frag)
        if key not in self._norm_cache:
            self._norm_cache[key] = normalize_tokens(frag.tokens)
        return self._norm_cache[key]