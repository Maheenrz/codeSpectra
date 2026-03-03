# detectors/type3/config/thresholds.py
"""
Detection thresholds for Type-3 clone detection.

ML thresholds are taken from the trained model's meta.json optimal_threshold
values per language. Hybrid thresholds are tuned for the weighted score
formula: winnowing*0.5 + AST*0.35 + metrics*0.15.
"""

# Per-language thresholds
# ml values derived from type3_unified_model.meta.json optimal_threshold
LANGUAGE_THRESHOLDS: dict[str, dict[str, float]] = {
    "java":       {"hybrid": 0.50, "ml": 0.382, "combined": 0.44},
    "cpp":        {"hybrid": 0.48, "ml": 0.362, "combined": 0.42},
    "c":          {"hybrid": 0.48, "ml": 0.362, "combined": 0.42},
    "python":     {"hybrid": 0.53, "ml": 0.402, "combined": 0.46},
    "javascript": {"hybrid": 0.50, "ml": 0.382, "combined": 0.44},
}

DEFAULT_THRESHOLDS: dict[str, float] = {
    "hybrid": 0.50,
    "ml":     0.382,
    "combined": 0.44,
}

# Confidence band cut-offs (applied to the combined 0-1 score)
CONFIDENCE_THRESHOLDS: dict[str, float] = {
    "HIGH":     0.75,
    "MEDIUM":   0.55,
    "LOW":      0.40,
    "UNLIKELY": 0.00,
}


def get_thresholds(language: str) -> dict[str, float]:
    return LANGUAGE_THRESHOLDS.get(language.lower(), DEFAULT_THRESHOLDS)


def get_confidence(combined_score: float) -> str:
    if combined_score >= CONFIDENCE_THRESHOLDS["HIGH"]:
        return "HIGH"
    if combined_score >= CONFIDENCE_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    if combined_score >= CONFIDENCE_THRESHOLDS["LOW"]:
        return "LOW"
    return "UNLIKELY"