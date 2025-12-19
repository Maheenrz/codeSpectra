from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseDetector(ABC):
    """
    Abstract Base Class for all clone detectors.
    Enforces that every detector has a 'detect' method.
    """
    def __init__(self):
        self.name = "Base Detector"

    @abstractmethod
    def detect(self, files: List[Dict[str, Any]], project_id: str) -> List[dict]:
        """
        Abstract method that must be implemented by all detectors.
        
        Args:
            files: List of dicts [{'path': '...', 'content': '...'}]
            project_id: ID of the current analysis session
            
        Returns:
            List of dicts representing clones found
        """
        pass