import hashlib
import re
from typing import List, Dict, Any
from detectors.base_detector import BaseDetector
from models.clone import CloneResult

class HashMethod(BaseDetector):
    """
    Type 1 Detector: Exact Matches using Hashing.
    Removes whitespace/comments and hashes the content.
    Speed: Fastest (O(1) lookup).
    """

    def __init__(self):
        super().__init__()
        self.name = "Hash-Based Exact Match"

    def normalize_code(self, code: str) -> str:
        """
        Remove whitespace and comments for Type 1 detection.
        """
        # Remove single line comments
        code = re.sub(r'//.*', '', code)
        # Remove multi-line comments (simple regex, can be improved)
        code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        # Remove whitespace
        code = re.sub(r'\s+', '', code)
        return code

    def detect(self, files: List[Dict[str, Any]], project_id: str) -> List[CloneResult]:
        """
        detects clones by hashing the normalized code content.
        """
        hashes = {}
        clones = []

        for file in files:
            file_path = file.get('path')
            content = file.get('content')
            
            if not content:
                continue

            # 1. Normalize
            normalized_content = self.normalize_code(content)
            
            # 2. Hash
            file_hash = hashlib.md5(normalized_content.encode('utf-8')).hexdigest()

            # 3. Check for collision (Clone found)
            if file_hash in hashes:
                original_file = hashes[file_hash]
                
                # Create Clone Result
                clone = CloneResult(
                    project_id=project_id,
                    file1=original_file,
                    file2=file_path,
                    clone_type=1,
                    method=self.name,
                    similarity=100.0,  # Hash match is always 100%
                    start_line1=1, end_line1=len(content.splitlines()), # Approximate
                    start_line2=1, end_line2=len(content.splitlines())
                )
                clones.append(clone)
            else:
                hashes[file_hash] = file_path

        return clones