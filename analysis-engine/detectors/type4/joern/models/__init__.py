# detectors/type4/joern/models/__init__.py

"""
Models for Type-4 Semantic Clone Detection
"""

from .pdg_models import (
    PDG,
    MethodPDG,
    PDGNode,
    PDGEdge,
    EdgeType,
    NodeType,
    ControlEdge,
    DataEdge
)

from .semantic_result import (
    SemanticCloneResult,
    SemanticScores,
    PDGInfo,
    ConfidenceLevel,
    BatchSemanticResult
)

__all__ = [
    # PDG Models
    'PDG',
    'MethodPDG',
    'PDGNode',
    'PDGEdge',
    'EdgeType',
    'NodeType',
    'ControlEdge',
    'DataEdge',
    
    # Result Models
    'SemanticCloneResult',
    'SemanticScores',
    'PDGInfo',
    'ConfidenceLevel',
    'BatchSemanticResult'
]