"""Type-3 detector configuration."""

from .extension_weights import get_file_weight, get_pair_weight, EXTENSION_WEIGHTS
from .thresholds import (
    HYBRID_WEIGHTS,
    COMBINED_HYBRID_WEIGHT,
    COMBINED_ML_WEIGHT,
    LANGUAGE_THRESHOLDS,
    DEFAULT_THRESHOLDS,
    CONFIDENCE_LEVELS,
)

__all__ = [
    'get_file_weight',
    'get_pair_weight',
    'EXTENSION_WEIGHTS',
    'HYBRID_WEIGHTS',
    'COMBINED_HYBRID_WEIGHT',
    'COMBINED_ML_WEIGHT',
    'LANGUAGE_THRESHOLDS',
    'DEFAULT_THRESHOLDS',
    'CONFIDENCE_LEVELS',
]