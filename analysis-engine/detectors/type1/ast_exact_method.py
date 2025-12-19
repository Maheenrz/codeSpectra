"""
Type 1 Clone Detection - Hybrid AST / Token Method
Uses real AST for Python, and Token Sequence matching for other languages.
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
    2. Others -> Uses Token Sequence (Universal Structural Match)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.min_lines = self.config.get('min_lines', 2)
        self.method_name = "AST Exact Match"
        
        # Regex to capture words (identifiers) or single symbols (operators)
        # This creates a "stream" of logic, ignoring whitespace entirely.
        self.token_pattern = re.compile(r'\w+|[^\w\s]')
    
    def detect_clones(self, code_fragments: List[Any]) -> Dict[str, Any]:
        # Hash table: structural_hash -> list of fragments
        structure_map = defaultdict(list)
        
        for fragment in code_fragments:
            # Skip small fragments
            if len(fragment.content.splitlines()) < self.min_lines:
                continue

            structural_hash = None
            
            # STRATEGY A: Real Python AST
            if fragment.language == 'python':
                structural_hash = self._generate_python_ast_hash(fragment.content)
                
            # STRATEGY B: Universal Token Sequence (for Java, C++, JS, etc.)
            else:
                structural_hash = self._generate_token_hash(fragment.content, fragment.language)
            
            # If we successfully generated a hash, store it
            if structural_hash:
                structure_map[structural_hash].append(fragment)

        # Find clones
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
            # dump() returns the string representation of the tree structure
            ast_str = ast.dump(tree, include_attributes=False)
            return hashlib.sha256(ast_str.encode('utf-8')).hexdigest()
        except SyntaxError:
            return None

    def _generate_token_hash(self, content: str, language: str) -> str:
        """
        Generates a hash based on the sequence of tokens.
        Effective 'AST-lite' for C++, Java, JS, etc.
        """
        # 1. Clean comments
        content = self._remove_comments(content)
        
        # 2. Extract tokens (keywords, variable names, operators)
        # e.g. "int a = 5;" -> ['int', 'a', '=', '5', ';']
        tokens = self.token_pattern.findall(content)
        
        if not tokens or len(tokens) < 3:
            return None
            
        # 3. Create a structural string (pipe-separated to preserve order)
        # "int|a|=|5|;"
        token_stream = "|".join(tokens)
        
        return hashlib.sha256(token_stream.encode('utf-8')).hexdigest()

    def _remove_comments(self, code: str) -> str:
        """Removes C-style and Python-style comments"""
        # Remove // comments
        code = re.sub(r'//.*', '', code)
        # Remove # comments
        code = re.sub(r'#.*', '', code)
        # Remove /* */ comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code