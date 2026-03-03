# detectors/type4/__init__.py
"""
Type-4 Semantic Clone Detector
Primary: Joern PDG-based (if Docker available)
Fallback: Custom regex-based PDG
"""
from detectors.type4.type4_detector import Type4Detector

__all__ = ["Type4Detector"]