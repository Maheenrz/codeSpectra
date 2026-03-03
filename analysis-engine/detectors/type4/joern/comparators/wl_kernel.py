# detectors/type4/joern/comparators/wl_kernel.py
"""
Weisfeiler-Lehman Graph Kernel for PDG Similarity

WL kernel is the standard method for comparing graphs whose nodes
carry labels (like PDGs where each node is a control/data/call node).

Algorithm (h iterations):
  1. Start with node label = semantic category  (CONTROL, LOOP, CALL …)
  2. Each iteration:
       new_label[v] = hash( label[v] + sorted(label[u] for u in neighbors(v)) )
  3. Similarity = Jaccard of the multisets of all labels seen across h rounds

Reference: Shervashidze et al., "Weisfeiler-Lehman Graph Kernels", JMLR 2011
"""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Dict, List, Optional, Set, Tuple

try:
    from ..models.pdg_models import PDG, PDGEdge, PDGNode, EdgeType
except ImportError:
    from models.pdg_models import PDG, PDGEdge, PDGNode, EdgeType


# ─── Node category for initial labelling ─────────────────────────────────────

_LABEL_MAP: Dict[str, str] = {
    "IF": "BRANCH", "ELSE": "BRANCH", "SWITCH": "BRANCH", "CASE": "BRANCH",
    "WHILE": "LOOP", "FOR": "LOOP", "DO": "LOOP", "FOREACH": "LOOP",
    "CALL": "CALL", "METHOD_CALL": "CALL",
    "RETURN": "RETURN",
    "ASSIGNMENT": "ASSIGN", "ASSIGN": "ASSIGN", "LOCAL": "ASSIGN",
    "LITERAL": "VALUE", "IDENTIFIER": "VALUE", "PARAMETER": "VALUE",
}

def _category(label: str) -> str:
    label_up = label.upper()
    for kw, cat in _LABEL_MAP.items():
        if kw in label_up:
            return cat
    return "OTHER"


def _short_hash(s: str) -> str:
    """8-char hex digest — compact but collision-resistant enough."""
    return hashlib.md5(s.encode()).hexdigest()[:8]


# ─── Core WL kernel ──────────────────────────────────────────────────────────

class WLKernel:
    """
    Weisfeiler-Lehman kernel for PDG comparison.

    Usage:
        kernel = WLKernel(h=3)
        similarity = kernel.similarity(pdg_a, pdg_b)
    """

    def __init__(self, h: int = 3):
        """
        Args:
            h: Number of WL iterations (3 is standard for code PDGs).
               More iterations = deeper neighbourhood comparison.
        """
        self.h = h

    # ── public ────────────────────────────────────────────────────────────────

    def similarity(self, pdg_a: PDG, pdg_b: PDG) -> float:
        """
        Return WL kernel similarity between two PDGs in [0, 1].
        """
        feat_a = self._wl_features(pdg_a)
        feat_b = self._wl_features(pdg_b)
        return self._jaccard(feat_a, feat_b)

    def feature_vector(self, pdg: PDG) -> Counter:
        """Return the WL feature multiset for a single PDG."""
        return self._wl_features(pdg)

    # ── internals ─────────────────────────────────────────────────────────────

    def _wl_features(self, pdg: PDG) -> Counter:
        """
        Run WL relabelling for self.h rounds across all methods in the PDG.
        Returns the combined label-multiset.
        """
        features: Counter = Counter()

        for method in pdg.methods:
            nodes = method.nodes
            edges = method.edges

            if not nodes:
                continue

            # Build adjacency: node_id → list of neighbour node_ids
            adj: Dict[str, List[str]] = {n.id: [] for n in nodes}
            for e in edges:
                if e.source_id in adj:
                    adj[e.source_id].append(e.target_id)
                # For undirected WL also add reverse (optional but helps PDG)
                if e.target_id in adj:
                    adj[e.target_id].append(e.source_id)

            # Initial labels from node semantic category
            labels: Dict[str, str] = {
                n.id: _category(n.label or "OTHER") for n in nodes
            }

            # Collect round-0 labels
            for lbl in labels.values():
                features[f"0:{lbl}"] += 1

            # WL iterations
            for iteration in range(1, self.h + 1):
                new_labels: Dict[str, str] = {}
                for node in nodes:
                    nid = node.id
                    neighbour_labels = sorted(
                        labels.get(nb, "OTHER") for nb in adj.get(nid, [])
                    )
                    concat = labels[nid] + "|" + ",".join(neighbour_labels)
                    new_labels[nid] = _short_hash(concat)

                labels = new_labels
                for lbl in labels.values():
                    features[f"{iteration}:{lbl}"] += 1

        return features

    @staticmethod
    def _jaccard(a: Counter, b: Counter) -> float:
        """Jaccard similarity of two label multisets."""
        all_keys: Set[str] = set(a.keys()) | set(b.keys())
        if not all_keys:
            return 1.0

        intersection = sum(min(a.get(k, 0), b.get(k, 0)) for k in all_keys)
        union        = sum(max(a.get(k, 0), b.get(k, 0)) for k in all_keys)
        return intersection / union if union else 0.0


# ── singleton convenience ─────────────────────────────────────────────────────

_kernel: Optional[WLKernel] = None

def get_wl_kernel(h: int = 3) -> WLKernel:
    global _kernel
    if _kernel is None or _kernel.h != h:
        _kernel = WLKernel(h=h)
    return _kernel