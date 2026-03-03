"""
Type 1 Clone Detection - String Method
========================================
Aggressive whitespace/comment normalization with direct string comparison.

FIX: No longer lowercases — case changes are Type-2, not Type-1.
Type-1 is strictly "identical code except whitespace and comments."
"""
import re
from typing import List, Dict


class Type1StringMethod:
    """
    Strategy 2: Aggressive normalization for Type-1 detection
    - Remove ALL comments (single-line, multi-line, docstrings)
    - Remove ALL whitespace (spaces, tabs, newlines)
    - Do NOT lowercase (case change = Type-2)
    - Direct string comparison (exact match after normalization)
    """

    def __init__(self, config: Dict):
        self.min_lines = config.get('min_lines', 2)
        self.method_name = "String Method"

    def aggressive_normalize(self, code: str) -> str:
        """
        Most aggressive normalization for Type-1.
        Strips comments and whitespace but preserves case and identifiers.
        """
        # Remove single-line comments
        code = re.sub(r'//[^\n]*', '', code)
        code = re.sub(
            r'#(?!include|define|pragma|ifndef|ifdef|endif|if|else|elif|undef)[^\n]*',
            '', code
        )

        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)

        # Remove ALL whitespace (spaces, tabs, newlines)
        code = re.sub(r'\s+', '', code)

        # DO NOT lowercase — case change is Type-2, not Type-1
        return code

    def detect_clones(self, fragments: List) -> Dict:
        """
        Compare normalized strings directly.
        Exact match after normalization = Type-1 clone.
        """
        matches = []

        normalized_fragments = []
        for frag in fragments:
            if len(frag.content.splitlines()) < self.min_lines:
                continue

            normalized = self.aggressive_normalize(frag.content)

            if not normalized or len(normalized) < 10:
                continue

            normalized_fragments.append({
                'file': frag.file_path,
                'file_id': frag.file_id,
                'start': frag.start_line,
                'end': frag.end_line,
                'type': frag.fragment_type,
                'normalized': normalized,
                'content': frag.content
            })

        for i in range(len(normalized_fragments)):
            for j in range(i + 1, len(normalized_fragments)):
                frag1 = normalized_fragments[i]
                frag2 = normalized_fragments[j]

                if frag1['normalized'] == frag2['normalized']:
                    matches.append({
                        'file1': frag1['file'],
                        'line1': frag1['start'],
                        'end1': frag1['end'],
                        'type1': frag1['type'],
                        'file2': frag2['file'],
                        'line2': frag2['start'],
                        'end2': frag2['end'],
                        'type2': frag2['type'],
                        'similarity': 100.0
                    })

        return {
            'method': self.method_name,
            'clones_found': len(matches),
            'matches': matches
        }