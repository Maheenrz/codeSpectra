"""
Type 1 Clone Detection - Hash Method
Normalizes code and uses SHA256 hashing for fast exact match detection
"""
import re
import hashlib
from typing import List, Dict
from collections import defaultdict


class Type1HashMethod:
    """
    Strategy 1: Hash-based Type 1 detection
    - Remove comments
    - Normalize whitespace
    - Generate SHA256 hash
    - Compare hashes
    """
    
    def __init__(self, config: Dict):
        self.min_lines = config.get('min_lines', 2)
        self.method_name = "Hash Method"
    
    def normalize_code(self, code: str) -> str:
        """
        Normalize code to ignore formatting differences
        """
        # Remove single-line comments (// and #)
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'#.*', '', code)
        
        # Remove multi-line comments (/* ... */)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove all whitespace and newlines
        code = re.sub(r'\s+', ' ', code)
        
        # Strip and lowercase for consistency
        code = code.strip().lower()
        
        return code
    
    def generate_hash(self, normalized_code: str) -> str:
        """Generate SHA256 hash of normalized code"""
        return hashlib.sha256(normalized_code.encode('utf-8')).hexdigest()
    
    def detect_clones(self, fragments: List) -> Dict:
        """
        Main detection logic
        Returns: dict with 'clones_found' and 'matches' list
        """
        # Hash table: hash -> list of fragments
        hash_table = defaultdict(list)
        
        for fragment in fragments:
            # Skip if too small
            if len(fragment.content.splitlines()) < self.min_lines:
                continue
            
            # Normalize and hash
            normalized = self.normalize_code(fragment.content)
            
            # Skip if empty after normalization
            if not normalized or len(normalized) < 10:
                continue
            
            code_hash = self.generate_hash(normalized)
            
            hash_table[code_hash].append({
                'file': fragment.file_path,
                'file_id': fragment.file_id,
                'start': fragment.start_line,
                'end': fragment.end_line,
                'type': fragment.fragment_type,
                'content': fragment.content
            })
        
        # Find duplicates (hashes with 2+ fragments)
        matches = []
        
        for code_hash, frags in hash_table.items():
            if len(frags) >= 2:
                # Generate all pairs
                for i in range(len(frags)):
                    for j in range(i + 1, len(frags)):
                        matches.append({
                            'file1': frags[i]['file'],
                            'line1': frags[i]['start'],
                            'end1': frags[i]['end'],
                            'type1': frags[i]['type'],
                            'file2': frags[j]['file'],
                            'line2': frags[j]['start'],
                            'end2': frags[j]['end'],
                            'type2': frags[j]['type'],
                            'similarity': 100.0,
                            'hash': code_hash[:12]  # Short hash for display
                        })
        
        return {
            'method': self.method_name,
            'clones_found': len(matches),
            'matches': matches
        }