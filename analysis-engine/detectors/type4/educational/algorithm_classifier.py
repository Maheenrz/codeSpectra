# detectors/type4/educational/algorithm_classifier.py
"""
Algorithm Signature Classifier for Type-4 Educational Detection.

Classifies a source file into:
  1. A PROBLEM CATEGORY  (e.g., SORT_ARRAY, STACK_OOP, FIBONACCI)
  2. An ALGORITHM FAMILY within that category (e.g., BUBBLE_SORT vs SELECTION_SORT)

This is the "algorithm signature" signal used in score fusion.

The classifier uses STATIC ANALYSIS only — it reads the source text and
applies regex + heuristic rules. No compilation or execution required.

Outputs:
  ClassificationResult
    .category       : str   — e.g. "SORT_ARRAY"   (or "" if unknown)
    .algorithm_family: str  — e.g. "BUBBLE_SORT"  (or "" if unknown)
    .confidence     : float — 0.0–1.0 how certain we are
    .signals        : dict  — evidence dict for logging/debugging
    .function_names : list  — detected function names
    .is_oop         : bool  — True if class-based implementation detected
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ClassificationResult:
    category:         str   = ""       # e.g. "SORT_ARRAY"
    algorithm_family: str   = ""       # e.g. "BUBBLE_SORT"
    confidence:       float = 0.0      # 0.0–1.0
    signals:          Dict[str, Any] = field(default_factory=dict)
    function_names:   List[str]      = field(default_factory=list)
    is_oop:           bool  = False    # OOP class vs procedural struct/functions
    detected_class:   str   = ""       # class/struct name if is_oop
    detected_methods: Dict[str, str] = field(default_factory=dict)
    # detected_methods maps logical role → actual name
    # e.g. {"push": "insertElement", "pop": "removeElement", ...}

    @property
    def is_known(self) -> bool:
        return bool(self.category)

    def __str__(self) -> str:
        if not self.is_known:
            return "AlgorithmClassifier: UNKNOWN"
        return (
            f"AlgorithmClassifier: category={self.category} "
            f"family={self.algorithm_family} "
            f"confidence={self.confidence:.2f} "
            f"oop={self.is_oop}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Regex patterns
# ─────────────────────────────────────────────────────────────────────────────

# C++ void function that takes (int[], int) — typical sort signature
_CPP_SORT_FUNC = re.compile(
    r'\bvoid\s+(\w+)\s*\('
    r'(?:'
    r'\s*int\s+\w+\s*\[\s*\]'       # int arr[]
    r'|'
    r'\s*int\s*\*\s*\w+'            # int* arr
    r')'
    r'\s*,\s*int\s+\w+\s*\)',
)

# C++ function that takes (int[], int, int) — search typically
_CPP_SEARCH_FUNC = re.compile(
    r'\bint\s+(\w+)\s*\('
    r'(?:'
    r'\s*int\s+\w+\s*\[\s*\]'
    r'|'
    r'\s*int\s*\*\s*\w+'
    r')'
    r'\s*,\s*int\s+\w+\s*,\s*int\s+\w+\s*\)',
)

# C++ long-returning function (single int arg) — fibonacci / factorial
_CPP_SINGLE_INT_FUNC = re.compile(
    r'\b(?:long\s+long|long|int)\s+(\w+)\s*\(\s*int\s+\w+\s*\)'
)

# C++ class definition
_CPP_CLASS = re.compile(r'\bclass\s+(\w+)\s*\{')

# C++ struct definition
_CPP_STRUCT = re.compile(r'\bstruct\s+(\w+)\s*\{')

# Python def
_PY_DEF = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)

# Java method
_JAVA_METHOD = re.compile(r'\bpublic\s+(?:static\s+)?(?:void|int|long|boolean)\s+(\w+)\s*\(')

# ─── keyword sets for category detection ──────────────────────────────────────

# Words commonly found in sorting implementations
_SORT_KEYWORDS = {
    "sort", "bubble", "selection", "insertion", "merge", "quick",
    "swap", "temp", "comparisons", "pass", "min", "minindex",
    "pivot", "partition",
}

# Words commonly found in stack implementations
_STACK_KEYWORDS = {
    "stack", "push", "pop", "peek", "top", "overflow", "underflow",
    "isempty", "isfull", "lifo", "isEmpty", "isFull",
}

# Words commonly found in queue implementations
_QUEUE_KEYWORDS = {
    "queue", "enqueue", "dequeue", "front", "rear", "circular",
    "head", "tail", "fifo",
}

# Words commonly found in linked list implementations
_LINKED_LIST_KEYWORDS = {
    "node", "next", "head", "tail", "insert", "delete", "traverse",
    "linked", "list", "append", "prepend", "singly", "doubly",
}

# Words for search
_SEARCH_KEYWORDS = {
    "search", "find", "linear", "binary", "sequential", "index",
    "target", "key", "found", "middle", "mid", "low", "high",
}

# Words for fibonacci
_FIBONACCI_KEYWORDS = {
    "fib", "fibonacci", "f(n)", "f(n-1)", "f(n-2)",
}

# Words for factorial
_FACTORIAL_KEYWORDS = {
    "factorial", "fact", "n!", "n *",
}

# Words for GCD
_GCD_KEYWORDS = {
    "gcd", "euclidean", "greatest", "common", "divisor", "hcf",
    "remainder", "modulo",
}

# Words for palindrome
_PALINDROME_KEYWORDS = {
    "palindrome", "reverse", "mirror", "symmetric",
}

# Words for string reverse
_REVERSE_KEYWORDS = {
    "reverse", "reversed", "reversestring", "reverse_str",
}


# ─────────────────────────────────────────────────────────────────────────────
# Algorithm family detection (within a category)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_sort_family(source: str) -> Tuple[str, float]:
    """
    Detect which sorting algorithm is used.
    Returns (family_name, confidence).
    """
    s = source.lower()

    # Bubble sort: adjacent comparison in nested loops
    has_adjacent_cmp = bool(re.search(r'\[\s*j\s*\]\s*>\s*\[\s*j\s*\+\s*1\s*\]', source)
                            or re.search(r'arr\[j\].*arr\[j\s*\+\s*1\]', source)
                            or re.search(r'data\[idx\].*data\[idx\s*\+\s*1\]', source))
    has_bubble_name = 'bubble' in s or 'bubblesort' in s or 'sortbubble' in s
    if has_adjacent_cmp or (has_bubble_name and 'for' in s):
        conf = 0.9 if has_adjacent_cmp else 0.7
        # Early-exit optimization (swap flag) = Usman's version
        if re.search(r'\bswapped\b|\bswap_flag\b|\bflag\b', s):
            return "BUBBLE_SORT_OPTIMIZED", conf
        return "BUBBLE_SORT", conf

    # Selection sort: find minimum index in inner loop
    has_min_idx = bool(re.search(r'\bmin\s*(?:index|idx|i|pos)\b', s, re.IGNORECASE)
                       or re.search(r'minIndex|minIdx|min_pos|min_j', source))
    has_selection_name = 'selection' in s or 'selectsort' in s or 'sortselect' in s
    if has_min_idx or has_selection_name:
        conf = 0.9 if has_min_idx else 0.7
        return "SELECTION_SORT", conf

    # Insertion sort: key variable, shift elements right
    has_key = bool(re.search(r'\bkey\s*=\s*(?:arr|data|numbers)', source))
    has_insertion_name = 'insertion' in s or 'insertsort' in s
    if has_key or has_insertion_name:
        conf = 0.85 if has_key else 0.65
        return "INSERTION_SORT", conf

    # Merge sort: recursive, merge function
    has_merge = bool(re.search(r'\bmerge\s*\(', source) and re.search(r'\bmergeSort\b|\bmerge_sort\b', source, re.IGNORECASE))
    if has_merge:
        return "MERGE_SORT", 0.9

    # Quick sort: pivot
    has_pivot = 'pivot' in s and 'partition' in s
    if has_pivot:
        return "QUICK_SORT", 0.9

    return "SORT_UNKNOWN", 0.4


def _detect_search_family(source: str) -> Tuple[str, float]:
    """Detect linear vs binary search."""
    s = source.lower()
    has_mid = bool(re.search(r'\bmid\b|\bmiddle\b', s))
    has_lo_hi = bool(re.search(r'\blow\b.*\bhigh\b|\bleft\b.*\bright\b', s))
    if has_mid or has_lo_hi:
        recursive = bool(re.search(r'\b(?:binarySearch|binary_search)\b.*\brecursive\b'
                                   r'|calls itself', s))
        return ("BINARY_SEARCH_RECURSIVE" if recursive else "BINARY_SEARCH_ITERATIVE"), 0.85
    return "LINEAR_SEARCH", 0.75


def _detect_fibonacci_family(source: str) -> Tuple[str, float]:
    s = source.lower()
    # Recursive: function calls itself
    has_recursion = bool(re.search(r'\bfib\s*\(\s*n\s*-\s*1\s*\)', s)
                         or re.search(r'\bfibonacci\s*\(\s*n\s*-\s*1\s*\)', s))
    has_loop = bool(re.search(r'\bfor\b|\bwhile\b', s))
    has_dp = bool(re.search(r'\bdp\b|\bmemo\b|\bcache\b|\btable\b', s))
    if has_dp:
        return "FIBONACCI_DP", 0.9
    if has_recursion:
        return "FIBONACCI_RECURSIVE", 0.9
    if has_loop:
        return "FIBONACCI_ITERATIVE", 0.9
    return "FIBONACCI_UNKNOWN", 0.4


def _detect_gcd_family(source: str) -> Tuple[str, float]:
    s = source.lower()
    has_recursion = bool(re.search(r'\bgcd\s*\(.*\)\s*;', source))
    has_modulo = '%' in source
    has_while = 'while' in s
    if has_modulo and has_while:
        return "GCD_EUCLIDEAN_ITERATIVE", 0.9
    if has_modulo and has_recursion:
        return "GCD_EUCLIDEAN_RECURSIVE", 0.9
    return "GCD_UNKNOWN", 0.4


# ─────────────────────────────────────────────────────────────────────────────
# OOP / Procedural detection helpers
# ─────────────────────────────────────────────────────────────────────────────

def _find_class_name(source: str) -> str:
    """Return first class name found, or '' if none."""
    m = _CPP_CLASS.search(source)
    return m.group(1) if m else ""


def _find_struct_name(source: str) -> str:
    """Return first struct name found (excluding Node/Element/etc.), or ''."""
    skip = {"node", "element", "item"}
    for m in _CPP_STRUCT.finditer(source):
        name = m.group(1).lower()
        if name not in skip:
            return m.group(1)
    return ""


def _detect_stack_methods(source: str) -> Dict[str, str]:
    """
    Detect push/pop/peek/isEmpty/size method/function names.
    Returns mapping: logical_role → actual_name_in_source.
    """
    roles: Dict[str, str] = {}
    s = source.lower()

    # Push: insert/push, modifies top
    push_candidates = re.findall(
        r'\bbool\s+(\w+)\s*\(\s*int\b'  # bool funcName(int
        r'|\bvoid\s+(\w+)\s*\(\s*int\b'  # void funcName(int
        r'|\bint\s+(\w+)\s*\(\s*int\b',  # int funcName(int
        source,
    )
    for groups in push_candidates:
        name = next(g for g in groups if g).lower()
        if any(kw in name for kw in ('push', 'insert', 'add', 'enqueue')):
            roles['push'] = next(g for g in groups if g)
            break

    # Pop: returns value, removes top
    pop_candidates = re.findall(r'\bint\s+(\w+)\s*\(\s*\)', source)
    for name in pop_candidates:
        lname = name.lower()
        if any(kw in lname for kw in ('pop', 'remove', 'delete', 'dequeue', 'extract')):
            roles['pop'] = name
            break

    # Peek: returns top without removing
    for name in pop_candidates:
        lname = name.lower()
        if any(kw in lname for kw in ('peek', 'top', 'front', 'head')):
            roles['peek'] = name
            break

    # Size
    for name in pop_candidates:
        lname = name.lower()
        if any(kw in lname for kw in ('size', 'count', 'length', 'len')):
            roles['size'] = name
            break

    # IsEmpty: returns bool
    bool_funcs = re.findall(r'\bbool\s+(\w+)\s*\(\s*\)', source)
    for name in bool_funcs:
        lname = name.lower()
        if 'empty' in lname or 'isempty' in lname:
            roles['isEmpty'] = name
            break

    return roles


def _detect_linked_list_methods(source: str) -> Dict[str, str]:
    """Detect insert/delete/search/length/display method names."""
    roles: Dict[str, str] = {}

    void_funcs = re.findall(r'\bvoid\s+(\w+)\s*\(', source)
    int_funcs  = re.findall(r'\bint\s+(\w+)\s*\(', source)
    bool_funcs = re.findall(r'\bbool\s+(\w+)\s*\(', source)

    for name in void_funcs:
        lname = name.lower()
        if any(kw in lname for kw in ('insertend', 'appendend', 'append', 'addend', 'insertatend')):
            roles['insert_end'] = name
        elif any(kw in lname for kw in ('insertfront', 'prepend', 'addfront', 'insertatfront')):
            roles['insert_front'] = name
        elif any(kw in lname for kw in ('delete', 'remove', 'erase')):
            roles['delete'] = name
        elif any(kw in lname for kw in ('display', 'print', 'show', 'traverse', 'printlist')):
            roles['print'] = name

    for name in int_funcs:
        lname = name.lower()
        if any(kw in lname for kw in ('length', 'size', 'count', 'len')):
            roles['length'] = name

    for name in bool_funcs:
        lname = name.lower()
        if any(kw in lname for kw in ('search', 'find', 'contains', 'exists')):
            roles['search'] = name

    # Also check void+bool returning 0/1
    for name in void_funcs:
        lname = name.lower()
        if any(kw in lname for kw in ('search', 'find', 'contains')):
            roles.setdefault('search', name)

    return roles


# ─────────────────────────────────────────────────────────────────────────────
# Main classifier
# ─────────────────────────────────────────────────────────────────────────────

def _keyword_score(source_lower: str, keywords: set) -> float:
    """Return fraction of keywords present in source (0.0–1.0)."""
    hits = sum(1 for kw in keywords if kw in source_lower)
    return hits / len(keywords) if keywords else 0.0


class AlgorithmClassifier:
    """
    Classifies a source file into a problem category and algorithm family.

    All classification is purely static — no compilation or execution.
    """

    # ── supported file extensions ─────────────────────────────────────────────
    _EXT_LANG: Dict[str, str] = {
        ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
        ".c":   "cpp",  # treat C as cpp for classification purposes
        ".h":   "cpp", ".hpp": "cpp",
        ".java": "java",
        ".py":   "python",
        ".js":   "javascript",
    }

    def classify_file(self, file_path: str) -> ClassificationResult:
        """
        Classify a source file.

        Args:
            file_path: Absolute path to the source file.

        Returns:
            ClassificationResult — always returns an object, never raises.
            On failure, result.is_known == False and signals contains error info.
        """
        path = Path(file_path)
        logger.debug("[Classifier] Classifying: %s", path.name)

        # ── safety: existence check ────────────────────────────────────────
        if not path.exists():
            logger.warning("[Classifier] File not found: %s", file_path)
            return ClassificationResult(signals={"error": "file_not_found"})

        # ── read source ────────────────────────────────────────────────────
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            logger.error("[Classifier] Cannot read %s: %s", file_path, exc)
            return ClassificationResult(signals={"error": str(exc)})

        lang = self._EXT_LANG.get(path.suffix.lower(), "")
        if not lang:
            logger.debug("[Classifier] Unsupported extension: %s", path.suffix)
            return ClassificationResult(signals={"error": "unsupported_extension"})

        return self._classify_source(source, lang, path.name)

    def _classify_source(
        self, source: str, lang: str, filename: str
    ) -> ClassificationResult:
        """Run all category-detection heuristics and pick the best match."""
        s = source.lower()
        signals: Dict[str, Any] = {"lang": lang, "filename": filename}

        # ── collect keyword scores ─────────────────────────────────────────
        scores = {
            "SORT":        _keyword_score(s, _SORT_KEYWORDS),
            "STACK":       _keyword_score(s, _STACK_KEYWORDS),
            "QUEUE":       _keyword_score(s, _QUEUE_KEYWORDS),
            "LINKED_LIST": _keyword_score(s, _LINKED_LIST_KEYWORDS),
            "SEARCH":      _keyword_score(s, _SEARCH_KEYWORDS),
            "FIBONACCI":   _keyword_score(s, _FIBONACCI_KEYWORDS),
            "FACTORIAL":   _keyword_score(s, _FACTORIAL_KEYWORDS),
            "GCD":         _keyword_score(s, _GCD_KEYWORDS),
            "PALINDROME":  _keyword_score(s, _PALINDROME_KEYWORDS),
            "REVERSE":     _keyword_score(s, _REVERSE_KEYWORDS),
        }
        signals["keyword_scores"] = {k: round(v, 3) for k, v in scores.items()}

    
        # ── structural signals ─────────────────────────────────────────────
        has_nested_loops = bool(re.search(r'for\s*\(.*\)\s*\{[^}]*for\s*\(', source, re.DOTALL))
        has_class        = bool(_CPP_CLASS.search(source)) if lang in ("cpp",) else False
        has_struct       = bool(_CPP_STRUCT.search(source)) if lang in ("cpp",) else False
        
        has_recursion = bool(re.search(r'(\w+)\s*\([^)]*\)\s*;.*\breturn\b.*\1\s*\(', source, re.DOTALL))
        
        signals.update({
            "has_nested_loops": has_nested_loops,
            "has_class": has_class,
            "has_struct": has_struct,
            "has_recursion": has_recursion,
        })


        # ── sort detection ─────────────────────────────────────────────────
        sort_funcs = [m.group(1) for m in _CPP_SORT_FUNC.finditer(source)]
        sort_confidence = scores["SORT"]
        if sort_funcs:
            sort_confidence = max(sort_confidence, 0.75)
        if has_nested_loops and scores["SORT"] > 0.1:
            sort_confidence = max(sort_confidence, 0.70)

        # ── search detection ───────────────────────────────────────────────
        search_funcs = [m.group(1) for m in _CPP_SEARCH_FUNC.finditer(source)]
        search_confidence = scores["SEARCH"]
        if search_funcs:
            search_confidence = max(search_confidence, 0.70)

        # ── fibonacci/factorial detection ──────────────────────────────────
        single_int_funcs = [m.group(1) for m in _CPP_SINGLE_INT_FUNC.finditer(source)]
        fib_confidence  = scores["FIBONACCI"]
        fact_confidence = scores["FACTORIAL"]
        for fname in single_int_funcs:
            fl = fname.lower()
            if 'fib' in fl:
                fib_confidence = max(fib_confidence, 0.80)
            if 'fact' in fl:
                fact_confidence = max(fact_confidence, 0.80)

        # ── GCD detection ─────────────────────────────────────────────────
        gcd_confidence = scores["GCD"]
        for fname in single_int_funcs:
            if 'gcd' in fname.lower() or 'hcf' in fname.lower():
                gcd_confidence = max(gcd_confidence, 0.85)

        # ── stack vs queue ─────────────────────────────────────────────────
        stack_confidence = scores["STACK"]
        # Distinguish stack from queue (queue has both front AND rear/tail)
        has_queue_tokens = bool(re.search(r'\bfront\b|\brear\b|\bdequeue\b|\benqueue\b', s))
        if has_queue_tokens:
            stack_confidence *= 0.5  # queue is more likely

        # ── linked list detection ──────────────────────────────────────────
        ll_confidence = scores["LINKED_LIST"]
        has_node_ptr  = bool(re.search(r'\bNode\s*\*|\bElement\s*\*', source))
        if has_node_ptr:
            ll_confidence = max(ll_confidence, 0.75)

        # ── pick best category ────────────────────────────────────────────
        candidates = {
            "SORT":        sort_confidence,
            "SEARCH":      search_confidence,
            "STACK":       stack_confidence,
            "LINKED_LIST": ll_confidence,
            "FIBONACCI":   fib_confidence,
            "FACTORIAL":   fact_confidence,
            "GCD":         gcd_confidence,
            "PALINDROME":  scores["PALINDROME"],
            "REVERSE":     scores["REVERSE"],
        }
        signals["candidates"] = {k: round(v, 3) for k, v in candidates.items()}

        best_key, best_conf = max(candidates.items(), key=lambda x: x[1])

        CONFIDENCE_THRESHOLD = 0.18   # minimum to claim a category
        if best_conf < CONFIDENCE_THRESHOLD:
            logger.info(
                "[Classifier] %s — below threshold (best=%s %.2f)",
                filename, best_key, best_conf,
            )
            return ClassificationResult(signals=signals)

        logger.info(
            "[Classifier] %s → %s (conf=%.2f)", filename, best_key, best_conf
        )

        # ── resolve into specific category and algorithm family ───────────
        return self._resolve(
            source, s, best_key, best_conf,
            sort_funcs, search_funcs, single_int_funcs,
            has_class, has_struct, signals,
        )

    def _resolve(
        self,
        source: str,
        s: str,         # source.lower()
        category_key: str,
        confidence: float,
        sort_funcs: List[str],
        search_funcs: List[str],
        single_int_funcs: List[str],
        has_class: bool,
        has_struct: bool,
        signals: Dict,
    ) -> ClassificationResult:
        """Map high-level category key to specific ClassificationResult."""

        # ── SORT ──────────────────────────────────────────────────────────
        if category_key == "SORT":
            family, family_conf = _detect_sort_family(source)
            merged_conf = (confidence + family_conf) / 2
            return ClassificationResult(
                category="SORT_ARRAY",
                algorithm_family=family,
                confidence=round(merged_conf, 3),
                signals=signals,
                function_names=sort_funcs,
            )

        # ── SEARCH ────────────────────────────────────────────────────────
        if category_key == "SEARCH":
            family, family_conf = _detect_search_family(source)
            cat = "BINARY_SEARCH" if "BINARY" in family else "LINEAR_SEARCH"
            return ClassificationResult(
                category=cat,
                algorithm_family=family,
                confidence=round((confidence + family_conf) / 2, 3),
                signals=signals,
                function_names=search_funcs,
            )

        # ── STACK ─────────────────────────────────────────────────────────
        if category_key == "STACK":
            methods = _detect_stack_methods(source)
            oop = has_class
            class_name = _find_class_name(source) if oop else _find_struct_name(source)
            cat = "STACK_OOP" if oop else "STACK_PROCEDURAL"
            return ClassificationResult(
                category=cat,
                algorithm_family="STACK_LIFO",
                confidence=round(confidence, 3),
                signals={**signals, "methods_found": list(methods.keys())},
                is_oop=oop,
                detected_class=class_name,
                detected_methods=methods,
            )

        # ── LINKED LIST ───────────────────────────────────────────────────
        if category_key == "LINKED_LIST":
            methods = _detect_linked_list_methods(source)
            oop = has_class
            class_name = _find_class_name(source) if oop else ""
            return ClassificationResult(
                category="LINKED_LIST",
                algorithm_family="LINKED_LIST_OOP" if oop else "LINKED_LIST_PROCEDURAL",
                confidence=round(confidence, 3),
                signals={**signals, "methods_found": list(methods.keys())},
                is_oop=oop,
                detected_class=class_name,
                detected_methods=methods,
            )

        # ── FIBONACCI ─────────────────────────────────────────────────────
        if category_key == "FIBONACCI":
            family, family_conf = _detect_fibonacci_family(source)
            return ClassificationResult(
                category="FIBONACCI",
                algorithm_family=family,
                confidence=round((confidence + family_conf) / 2, 3),
                signals=signals,
                function_names=single_int_funcs,
            )

        # ── FACTORIAL ─────────────────────────────────────────────────────
        if category_key == "FACTORIAL":
            recursive = bool(re.search(r'\bfact(?:orial)?\s*\(.*n\s*-\s*1\s*\)', s))
            return ClassificationResult(
                category="FACTORIAL",
                algorithm_family="FACTORIAL_RECURSIVE" if recursive else "FACTORIAL_ITERATIVE",
                confidence=round(confidence, 3),
                signals=signals,
                function_names=single_int_funcs,
            )

        # ── GCD ───────────────────────────────────────────────────────────
        if category_key == "GCD":
            family, family_conf = _detect_gcd_family(source)
            return ClassificationResult(
                category="GCD",
                algorithm_family=family,
                confidence=round((confidence + family_conf) / 2, 3),
                signals=signals,
                function_names=single_int_funcs,
            )

        # ── PALINDROME ────────────────────────────────────────────────────
        if category_key == "PALINDROME":
            return ClassificationResult(
                category="IS_PALINDROME",
                algorithm_family="PALINDROME_TWO_POINTER",
                confidence=round(confidence, 3),
                signals=signals,
            )

        # ── REVERSE ───────────────────────────────────────────────────────
        if category_key == "REVERSE":
            return ClassificationResult(
                category="STRING_REVERSE",
                algorithm_family="STRING_REVERSE_ITERATIVE",
                confidence=round(confidence, 3),
                signals=signals,
            )

        # Fallback
        return ClassificationResult(signals=signals)


# ── singleton ─────────────────────────────────────────────────────────────────

_classifier: Optional[AlgorithmClassifier] = None


def get_classifier() -> AlgorithmClassifier:
    global _classifier
    if _classifier is None:
        _classifier = AlgorithmClassifier()
    return _classifier