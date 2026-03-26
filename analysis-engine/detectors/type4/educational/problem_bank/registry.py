# detectors/type4/educational/problem_bank/registry.py
"""
Problem Registry — maps problem categories to test banks.

The registry is the single source of truth for:
  - Which test cases belong to which category
  - Which categories are supported for I/O testing
  - Metadata about each category (display name, description)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .test_cases import (
    SORT_ARRAY, STACK_OPERATIONS, LINKED_LIST_OPERATIONS,
    LINEAR_SEARCH, BINARY_SEARCH, FIBONACCI, FACTORIAL,
    GCD, IS_PALINDROME, STRING_REVERSE,
)

logger = logging.getLogger(__name__)

TestCase = Tuple[str, str]  # (stdin_input, expected_stdout)


@dataclass
class ProblemCategory:
    """Metadata and test cases for one problem category."""
    name:        str
    display:     str
    description: str
    test_cases:  List[TestCase]
    # Algorithm families that fall under this category.
    # Used by the algorithm classifier to confirm category assignment.
    algorithm_families: List[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.test_cases)


# ─── Category definitions ─────────────────────────────────────────────────────

_CATEGORIES: List[ProblemCategory] = [
    ProblemCategory(
        name="SORT_ARRAY",
        display="Sort Array",
        description="Any sorting algorithm operating on an integer array",
        test_cases=SORT_ARRAY,
        algorithm_families=[
            "BUBBLE_SORT", "SELECTION_SORT", "INSERTION_SORT",
            "MERGE_SORT", "QUICK_SORT", "COUNTING_SORT",
        ],
    ),
    ProblemCategory(
        name="STACK_OOP",
        display="Stack (OOP)",
        description="Stack data structure implemented as a class",
        test_cases=STACK_OPERATIONS,
        algorithm_families=["STACK_LIFO"],
    ),
    ProblemCategory(
        name="STACK_PROCEDURAL",
        display="Stack (Procedural)",
        description="Stack data structure implemented with a struct and standalone functions",
        test_cases=STACK_OPERATIONS,
        algorithm_families=["STACK_LIFO"],
    ),
    ProblemCategory(
        name="LINKED_LIST",
        display="Linked List",
        description="Singly linked list with insert/delete/search/print operations",
        test_cases=LINKED_LIST_OPERATIONS,
        algorithm_families=["LINKED_LIST_SINGLY", "LINKED_LIST_OOP", "LINKED_LIST_PROCEDURAL"],
    ),
    ProblemCategory(
        name="LINEAR_SEARCH",
        display="Linear Search",
        description="Find element in unsorted array by scanning sequentially",
        test_cases=LINEAR_SEARCH,
        algorithm_families=["LINEAR_SEARCH"],
    ),
    ProblemCategory(
        name="BINARY_SEARCH",
        display="Binary Search",
        description="Find element in sorted array using divide and conquer",
        test_cases=BINARY_SEARCH,
        algorithm_families=["BINARY_SEARCH", "BINARY_SEARCH_RECURSIVE", "BINARY_SEARCH_ITERATIVE"],
    ),
    ProblemCategory(
        name="FIBONACCI",
        display="Fibonacci",
        description="Compute the nth Fibonacci number",
        test_cases=FIBONACCI,
        algorithm_families=["FIBONACCI_RECURSIVE", "FIBONACCI_ITERATIVE", "FIBONACCI_DP"],
    ),
    ProblemCategory(
        name="FACTORIAL",
        display="Factorial",
        description="Compute n!",
        test_cases=FACTORIAL,
        algorithm_families=["FACTORIAL_RECURSIVE", "FACTORIAL_ITERATIVE"],
    ),
    ProblemCategory(
        name="GCD",
        display="GCD",
        description="Compute the greatest common divisor of two integers",
        test_cases=GCD,
        algorithm_families=["GCD_EUCLIDEAN", "GCD_ITERATIVE", "GCD_RECURSIVE"],
    ),
    ProblemCategory(
        name="IS_PALINDROME",
        display="Palindrome Check",
        description="Check whether a string reads the same forwards and backwards",
        test_cases=IS_PALINDROME,
        algorithm_families=["PALINDROME_TWO_POINTER", "PALINDROME_REVERSE"],
    ),
    ProblemCategory(
        name="STRING_REVERSE",
        display="String Reverse",
        description="Reverse a string",
        test_cases=STRING_REVERSE,
        algorithm_families=["STRING_REVERSE_ITERATIVE", "STRING_REVERSE_RECURSIVE"],
    ),
]


class ProblemRegistry:
    """
    Registry of all supported problem categories and their test banks.

    Usage:
        registry = get_registry()
        cat = registry.get("SORT_ARRAY")
        for stdin_in, expected_out in cat.test_cases:
            ...
    """

    def __init__(self) -> None:
        self._map: Dict[str, ProblemCategory] = {
            cat.name: cat for cat in _CATEGORIES
        }
        logger.debug(
            "[ProblemRegistry] Loaded %d categories: %s",
            len(self._map),
            ", ".join(self._map.keys()),
        )

    # ── public API ────────────────────────────────────────────────────────────

    def get(self, category_name: str) -> Optional[ProblemCategory]:
        """Return the ProblemCategory object, or None if not found."""
        cat = self._map.get(category_name)
        if cat is None:
            logger.debug("[ProblemRegistry] Unknown category: %s", category_name)
        return cat

    def all_names(self) -> List[str]:
        """All registered category names."""
        return list(self._map.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._map

    def __len__(self) -> int:
        return len(self._map)

    def summary(self) -> str:
        lines = [f"ProblemRegistry — {len(self)} categories:"]
        for cat in _CATEGORIES:
            lines.append(f"  {cat.name:25s} {len(cat):3d} test cases  — {cat.description}")
        return "\n".join(lines)


# ── singleton ─────────────────────────────────────────────────────────────────

_registry: Optional[ProblemRegistry] = None


def get_registry() -> ProblemRegistry:
    global _registry
    if _registry is None:
        _registry = ProblemRegistry()
    return _registry
