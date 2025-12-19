"""
Type 1 Clone Detection - String Method
Aggressive normalization with direct string comparison
"""
import re
from typing import List, Dict


class Type1StringMethod:
    """
    Strategy 2: Aggressive string normalization
    - Remove ALL whitespace
    - Remove ALL comments
    - Lowercase everything
    - Direct string comparison
    """
    
    def __init__(self, config: Dict):
        self.min_lines = config.get('min_lines', 2)
        self.method_name = "String Method"
    
    def aggressive_normalize(self, code: str) -> str:
        """
        Most aggressive normalization possible
        """
        # Remove single-line comments
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'#.*', '', code)
        
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Remove ALL whitespace (spaces, tabs, newlines)
        code = re.sub(r'\s+', '', code)
        
        # Lowercase
        code = code.lower()
        
        return code
    
    def detect_clones(self, fragments: List) -> Dict:
        """
        Compare normalized strings directly
        """
        matches = []
        
        # Pre-normalize all fragments
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
        
        # Pairwise comparison
        for i in range(len(normalized_fragments)):
            for j in range(i + 1, len(normalized_fragments)):
                frag1 = normalized_fragments[i]
                frag2 = normalized_fragments[j]
                
                # Exact string match
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