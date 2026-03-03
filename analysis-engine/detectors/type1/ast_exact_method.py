"""
Type 1 Clone Detection - Hybrid AST / Token Method
====================================================
Uses real AST for Python, and Token Sequence matching for other languages.

FIX: Token hash now preserves case for non-Python languages.
     For Python, ast.dump already ignores variable names at the
     structure level, so the Python AST path is fine as-is.
     For C++/Java/JS, the token stream MUST preserve case because
     changing a variable name from 'Node' to 'Element' is Type-2.

     The old code included raw variable names in the token hash,
     which was actually correct for Type-1 (exact match). The fix
     here is just ensuring comment removal is consistent.
"""
import ast
import hashlib
import re
from typing import List, Dict, Any
from collections import defaultdict


class Type1ASTMethod:
    """
    Hybrid Structural Detection:
    1. Python -> Uses real Abstract Syntax Tree (ast module)
    2. Others -> Uses Token Sequence hash (preserves case)
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.min_lines = self.config.get('min_lines', 2)
        self.method_name = "AST Exact Match"

        # Regex to capture words (identifiers) or single symbols (operators)
        self.token_pattern = re.compile(r'\w+|[^\w\s]')

    def detect_clones(self, code_fragments: List[Any]) -> Dict[str, Any]:
        structure_map = defaultdict(list)

        for fragment in code_fragments:
            if len(fragment.content.splitlines()) < self.min_lines:
                continue

            structural_hash = None

            # STRATEGY A: Real Python AST
            if fragment.language == 'python':
                structural_hash = self._generate_python_ast_hash(fragment.content)

            # STRATEGY B: Token Sequence for C++, Java, JS, etc.
            else:
                structural_hash = self._generate_token_hash(
                    fragment.content, fragment.language
                )

            if structural_hash:
                structure_map[structural_hash].append(fragment)

        matches = []
        for s_hash, frags in structure_map.items():
            if len(frags) < 2:
                continue

            for i in range(len(frags)):
                for j in range(i + 1, len(frags)):
                    matches.append({
                        "file1": frags[i].file_path,
                        "line1": frags[i].start_line,
                        "end1": frags[i].end_line,
                        "type1": frags[i].fragment_type,
                        "file2": frags[j].file_path,
                        "line2": frags[j].start_line,
                        "end2": frags[j].end_line,
                        "type2": frags[j].fragment_type,
                        "similarity": 100,
                        "structural_hash": s_hash[:12]
                    })

        return {
            "method_name": self.method_name,
            "clones_found": len(matches),
            "matches": matches
        }

    def _generate_python_ast_hash(self, content: str) -> str:
        """Parses Python code to AST and hashes the dump."""
        try:
            tree = ast.parse(content)
            ast_str = ast.dump(tree, include_attributes=False)
            return hashlib.sha256(ast_str.encode('utf-8')).hexdigest()
        except SyntaxError:
            return None

    def _generate_token_hash(self, content: str, language: str) -> str:
        """
        Generates a hash based on the sequence of tokens.
        Preserves case — 'Node' and 'Element' produce different hashes.
        """
        content = self._remove_comments(content)

        tokens = self.token_pattern.findall(content)

        if not tokens or len(tokens) < 3:
            return None

        # Pipe-separated to preserve order, case preserved
        token_stream = "|".join(tokens)

        return hashlib.sha256(token_stream.encode('utf-8')).hexdigest()

    def _remove_comments(self, code: str) -> str:
        """Removes comments but preserves preprocessor directives."""
        # Remove // comments
        code = re.sub(r'//[^\n]*', '', code)
        # Remove # comments (but NOT #include, #define, etc.)
        code = re.sub(
            r'#(?!include|define|pragma|ifndef|ifdef|endif|if|else|elif|undef)[^\n]*',
            '', code
        )
        # Remove /* */ comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code