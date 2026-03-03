# detectors/type3/clone_clusterer.py
"""
Clone Clusterer — Transitive Closure Grouping
================================================
Groups overlapping clone pairs into clone classes using
union-find (disjoint-set) transitive closure.

A clone class is a set of fragments where every member
is directly or transitively similar to at least one other member.

Example:
  If fragment A ~ fragment B and fragment B ~ fragment C,
  then {A, B, C} form one clone class even if A and C
  are not directly similar.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Any


# ── Union-Find ───────────────────────────────────────────────────────────────

class _UnionFind:
    def __init__(self):
        self._parent: Dict[str, str] = {}
        self._rank:   Dict[str, int] = {}

    def _make(self, x: str):
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x]   = 0

    def find(self, x: str) -> str:
        self._make(x)
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])  # path compression
        return self._parent[x]

    def union(self, x: str, y: str):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1


# ── Clone class dataclass ────────────────────────────────────────────────────

@dataclass
class CloneClass:
    class_id:   int
    members:    List[Dict]          # {file_path, name, start_line, end_line}
    pairs:      List[Dict]          # {frag_a, frag_b, similarity}
    max_sim:    float = 0.0
    avg_sim:    float = 0.0

    def to_dict(self) -> Dict:
        return {
            "class_id":    self.class_id,
            "size":        len(self.members),
            "max_sim":     self.max_sim,
            "avg_sim":     self.avg_sim,
            "members":     self.members,
            "pairs":       self.pairs,
        }


# ── Clusterer ────────────────────────────────────────────────────────────────

class CloneClusterer:
    """
    Groups fragment-level clone pairs into clone classes via
    transitive closure (union-find).
    """

    def cluster(
        self,
        pairs: List[Dict],   # each has frag_a, frag_b, similarity
        min_similarity: float = 0.70,
    ) -> List[CloneClass]:
        """
        Args:
            pairs: list of dicts with keys:
                   frag_a, frag_b  → Fragment objects or dicts with
                                     file_path/name/start_line/end_line
                   similarity      → float
            min_similarity: only cluster pairs above this threshold

        Returns:
            Sorted list of CloneClass (largest first).
        """
        uf = _UnionFind()
        valid_pairs = [p for p in pairs if p["similarity"] >= min_similarity]

        # Build union-find
        for p in valid_pairs:
            key_a = self._frag_key(p["frag_a"])
            key_b = self._frag_key(p["frag_b"])
            uf.union(key_a, key_b)

        # Group pairs by root
        from collections import defaultdict
        root_to_frags: Dict[str, Set[str]]  = defaultdict(set)
        root_to_pairs: Dict[str, List[Dict]] = defaultdict(list)
        frag_meta:     Dict[str, Dict]       = {}

        for p in valid_pairs:
            key_a = self._frag_key(p["frag_a"])
            key_b = self._frag_key(p["frag_b"])
            root  = uf.find(key_a)
            root_to_frags[root].add(key_a)
            root_to_frags[root].add(key_b)
            root_to_pairs[root].append(p)
            frag_meta[key_a] = self._frag_dict(p["frag_a"])
            frag_meta[key_b] = self._frag_dict(p["frag_b"])

        # Build CloneClass objects
        classes: List[CloneClass] = []
        for cid, (root, frag_keys) in enumerate(root_to_frags.items()):
            cpairs = root_to_pairs[root]
            sims   = [p["similarity"] for p in cpairs]
            classes.append(CloneClass(
                class_id = cid,
                members  = [frag_meta[k] for k in frag_keys],
                pairs    = [
                    {
                        "frag_a":     self._frag_dict(p["frag_a"]),
                        "frag_b":     self._frag_dict(p["frag_b"]),
                        "similarity": p["similarity"],
                    }
                    for p in cpairs
                ],
                max_sim  = round(max(sims), 4),
                avg_sim  = round(sum(sims) / len(sims), 4),
            ))

        # Sort: largest class first, then by similarity
        classes.sort(key=lambda c: (len(c.members), c.max_sim), reverse=True)
        return classes

    @staticmethod
    def _frag_key(frag) -> str:
        """Stable unique key for a fragment."""
        if isinstance(frag, dict):
            return f"{frag.get('file_path','')}::{frag.get('name','')}::{frag.get('start_line',0)}"
        return f"{frag.file_path}::{frag.name}::{frag.start_line}"

    @staticmethod
    def _frag_dict(frag) -> Dict:
        if isinstance(frag, dict):
            return frag
        return {
            "file_path":  frag.file_path,
            "name":       frag.name,
            "start_line": frag.start_line,
            "end_line":   frag.end_line,
        }