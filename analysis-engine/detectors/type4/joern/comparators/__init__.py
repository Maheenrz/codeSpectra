# detectors/type4/joern/comparators/__init__.py

"""
Comparators for Type-4 Semantic Clone Detection
"""

from .semantic_analyzer import (
    SemanticAnalyzer,
    get_semantic_analyzer
)

__all__ = [
    'SemanticAnalyzer',
    'get_semantic_analyzer'
]