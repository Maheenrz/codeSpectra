# detectors/type3/winnowing.py
"""
Winnowing Fingerprinting for Code Clone Detection
===================================================
Implements the Winnowing algorithm (Schleimer, Wilkerson & Aiken, 2003)
for document fingerprinting.

Pipeline:
  1. Hash every k-gram (contiguous k-token window) using MD5
  2. Slide a window of size w over the hash list
  3. Keep the minimum hash in each window → fingerprint set
  4. Compare fingerprint sets via Jaccard similarity

This gives a position-independent measure of shared code fragments.
"""

import hashlib

WINNOWING_K = 7
WINNOWING_W = 4


class WinnowingDetector:
    def __init__(self, k: int = WINNOWING_K, window_size: int = WINNOWING_W):
        self.k = k
        self.w = window_size

    def _get_hashes(self, tokens: list) -> list:
        """Hash every k-gram in the token stream."""
        hashes = []
        for i in range(len(tokens) - self.k + 1):
            gram = "|".join(tokens[i : i + self.k])
            h = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
            hashes.append(h)
        return hashes

    def get_fingerprint(self, tokens: list) -> set:
        """
        Winnowing: slide a window of size w over the hash list and
        keep the minimum hash in each window (robust minimum selection).
        Returns a set of fingerprint hashes.
        """
        hashes = self._get_hashes(tokens)
        fingerprints = set()
        for i in range(len(hashes) - self.w + 1):
            frame = hashes[i : i + self.w]
            fingerprints.add(min(frame))
        return fingerprints

    def calculate_similarity(self, set_a: set, set_b: set) -> float:
        """Jaccard similarity between two fingerprint sets."""
        if not set_a or not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union)