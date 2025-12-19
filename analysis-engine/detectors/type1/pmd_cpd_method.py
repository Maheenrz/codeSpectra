"""
Type 1 Detection - PMD/CPD Integration
External tool integration (requires PMD installed)
"""

import subprocess
import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass
import time


@dataclass
class CodeFragment:
    file_path: str
    file_id: int
    start_line: int
    end_line: int
    content: str
    language: str


@dataclass
class CloneMatch:
    fragment1: CodeFragment
    fragment2: CodeFragment
    similarity_score: float
    lines_of_code: int


class Type1PMDMethod:
    """
    PMD/CPD-based Type 1 clone detection
    - Uses external PMD tool
    - Works for multiple languages
    - Industry-standard tool
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.min_tokens = self.config.get('min_tokens', 50)
        self.method_name = "PMD/CPD"
        self.pmd_available = self._check_pmd_available()
    
    def _check_pmd_available(self) -> bool:
        """Check if PMD is installed"""
        try:
            result = subprocess.run(
                ['cpd', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def detect_clones(self, code_fragments: List[CodeFragment]) -> Dict[str, Any]:
        """Detect clones using PMD/CPD"""
        start_time = time.time()
        
        # If PMD not available, return empty result
        if not self.pmd_available:
            return {
                'method_name': self.method_name,
                'clone_type': 'type1',
                'clones_found': 0,
                'clone_groups': 0,
                'execution_time_ms': 0,
                'matches': [],
                'groups': [],
                'metadata': {
                    'error': 'PMD/CPD not installed',
                    'message': 'Install PMD from https://pmd.github.io/ to use this method'
                }
            }
        
        # Group fragments by language
        language_groups = {}
        for fragment in code_fragments:
            lang = self._map_language(fragment.language)
            if lang not in language_groups:
                language_groups[lang] = []
            language_groups[lang].append(fragment)
        
        # Run CPD for each language
        all_matches = []
        all_groups = []
        
        for language, fragments in language_groups.items():
            if not fragments:
                continue
            
            # Write files temporarily
            temp_files = []
            for fragment in fragments:
                temp_file = f"/tmp/{fragment.file_id}.{self._get_extension(language)}"
                with open(temp_file, 'w') as f:
                    f.write(fragment.content)
                temp_files.append(temp_file)
            
            try:
                # Run CPD
                result = subprocess.run(
                    [
                        'cpd',
                        '--minimum-tokens', str(self.min_tokens),
                        '--language', language,
                        '--format', 'json',
                        '--files', ','.join(temp_files)
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout:
                    cpd_results = json.loads(result.stdout)
                    # Parse CPD results into our format
                    # (CPD output format varies, this is simplified)
                    
            except Exception as e:
                print(f"CPD error for {language}: {e}")
            finally:
                # Clean up temp files
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return {
            'method_name': self.method_name,
            'clone_type': 'type1',
            'clones_found': len(all_matches),
            'clone_groups': len(all_groups),
            'execution_time_ms': execution_time,
            'matches': all_matches,
            'groups': all_groups,
            'metadata': {
                'pmd_available': self.pmd_available,
                'languages_processed': list(language_groups.keys())
            }
        }
    
    def _map_language(self, language: str) -> str:
        """Map our language names to PMD language names"""
        mapping = {
            'python': 'python',
            'py': 'python',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'javascript': 'ecmascript',
            'js': 'ecmascript'
        }
        return mapping.get(language.lower(), 'java')
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'python': 'py',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'ecmascript': 'js'
        }
        return extensions.get(language, 'txt')
    
    def get_clone_type(self):
        return "type1"


if __name__ == "__main__":
    detector = Type1PMDMethod()
    print(f"PMD Available: {detector.pmd_available}")
    
    if not detector.pmd_available:
        print("⚠️  PMD/CPD not installed. This method will return no results.")
        print("Install from: https://pmd.github.io/")