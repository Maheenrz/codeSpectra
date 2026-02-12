# analysis-engine/detectors/type4/__init__.py

"""
Type-4 Semantic Clone Detection using Simplified PDG (Program Dependence Graph)

This module detects code clones that have:
- Different syntax
- Different algorithms
- But SAME semantic behavior (produce same output)

Supported Languages: C++, C, Java, Python
"""

from .pdg_detector import Type4PDGDetector, Type4ResultWrapper

__all__ = ['Type4PDGDetector', 'Type4ResultWrapper']
__version__ = '1.0.0'