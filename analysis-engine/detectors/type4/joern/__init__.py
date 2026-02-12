# detectors/type4/joern/__init__.py

"""
Joern Type-4 Semantic Clone Detection Module

This module provides semantic (Type-4) code clone detection using
Joern's Program Dependence Graph (PDG) analysis.

Type-4 clones are code fragments with:
- Same functionality/behavior
- Different implementation

Supported Languages:
- Python, Java, JavaScript, C, C++, Go, PHP

Usage:
    from joern import JoernDetector
    
    detector = JoernDetector()
    result = detector.detect(code1, code2, language="python")
    
    if result.is_semantic_clone:
        print(f"Semantic clone! Similarity: {result.similarity:.1%}")
"""

__version__ = "2.0.0"

# Main detector
from .joern_detector import JoernDetector, get_joern_detector

# Client
from .client import (
    JoernClient,
    JoernContainerManager,
    DockerConnectionError,
    get_container_manager
)

# Comparators
from .comparators import (
    SemanticAnalyzer,
    get_semantic_analyzer
)

# Models
from .models import (
    # PDG Models
    PDG,
    MethodPDG,
    PDGNode,
    PDGEdge,
    EdgeType,
    NodeType,
    
    # Result Models
    SemanticCloneResult,
    SemanticScores,
    PDGInfo,
    ConfidenceLevel,
    BatchSemanticResult
)

# Config
from .config import (
    Config,
    get_config,
    get_docker_config,
    get_joern_config,
    get_semantic_config
)

__all__ = [
    # Version
    "__version__",
    
    # Main Detector
    "JoernDetector",
    "get_joern_detector",
    
    # Client
    "JoernClient",
    "JoernContainerManager",
    "DockerConnectionError",
    "get_container_manager",
    
    # Comparators
    "SemanticAnalyzer",
    "get_semantic_analyzer",
    
    # PDG Models
    "PDG",
    "MethodPDG",
    "PDGNode",
    "PDGEdge",
    "EdgeType",
    "NodeType",
    
    # Result Models
    "SemanticCloneResult",
    "SemanticScores",
    "PDGInfo",
    "ConfidenceLevel",
    "BatchSemanticResult",
    
    # Config
    "Config",
    "get_config",
    "get_docker_config",
    "get_joern_config",
    "get_semantic_config"
]