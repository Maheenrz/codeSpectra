# detectors/type3/config/extension_weights.py
"""
File extension weights for Type-3 plagiarism detection.

For student assignments the .h / .hpp header files almost always contain
identical or near-identical boilerplate (include guards, class declarations,
function signatures). Treating them at full weight inflates similarity scores
for every student pair and produces false positives.

Primary implementation files (.cpp, .java, .py, .js) carry full weight.
Header / interface / declaration files carry a reduced weight.
TypeScript carries a small reduction because type annotations add syntactic
bulk that is often identical across students following the same type hints.
"""

from pathlib import Path

# Weight per extension (applied to the combined similarity score)
EXTENSION_WEIGHTS: dict[str, float] = {
    # Implementation files - full weight
    ".cpp": 1.00,
    ".cc":  1.00,
    ".cxx": 1.00,
    ".c":   1.00,
    ".java": 1.00,
    ".py": 1.00,
    ".js":  1.00,
    ".ts":  1.00,
    # Header files - ZERO weight (exclude from comparison)
    # These cause false positives due to boilerplate code
    ".h":   0.00,   # Changed from 0.35 to 0.00
    ".hpp": 0.00,   # Changed from 0.35 to 0.00
    ".hxx": 0.00,   # Changed from 0.35 to 0.00
}

DEFAULT_WEIGHT: float = 0.80  # unknown extensions get a small penalty


def get_extension_weight(file_path: str) -> float:
    """Return the weight for a single file based on its extension."""
    ext = Path(file_path).suffix.lower()
    return EXTENSION_WEIGHTS.get(ext, DEFAULT_WEIGHT)


def get_pair_weight(file_a: str, file_b: str) -> float:
    """
    Return the effective weight for a comparison between two files.

    Uses the LOWER of the two weights: if either file is a low-significance
    type (e.g. a .h header), the whole comparison is discounted because the
    high similarity is expected and not indicative of plagiarism.
    """
    wa = get_extension_weight(file_a)
    wb = get_extension_weight(file_b)
    # If either is a header (weight 0), skip comparison entirely
    if wa == 0 or wb == 0:
        return 0.0
    return min(wa, wb)