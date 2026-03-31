"""
Educational Type-4 detection module.
"""
from .educational_detector import EducationalType4Detector
from .algorithm_classifier import AlgorithmClassifier, get_classifier, ClassificationResult
from .io_behavioral_tester import IOBehavioralTester, get_tester, IOBehavioralResult
from .score_fusion import FusionInput, FusionResult, fuse_scores

__all__ = [
    "EducationalType4Detector",
    "AlgorithmClassifier", "get_classifier", "ClassificationResult",
    "IOBehavioralTester", "get_tester", "IOBehavioralResult",
    "FusionInput", "FusionResult", "fuse_scores",
]
