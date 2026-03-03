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
    # C / C++
    ".cpp": 1.00,
    ".cc":  1.00,
    ".cxx": 1.00,
    ".c":   1.00,
    ".h":   0.35,   # header — nearly always boilerplate
    ".hpp": 0.35,
    ".hxx": 0.35,

    # Java
    ".java": 1.00,

    # Python
    ".py": 1.00,

    # JavaScript / TypeScript
    ".js":  1.00,
    ".jsx": 0.90,
    ".ts":  0.85,   # type annotations inflate apparent similarity
    ".tsx": 0.85,
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
    return min(wa, wb)