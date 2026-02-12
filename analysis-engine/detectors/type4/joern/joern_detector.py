# detectors/type4/joern/joern_detector.py

"""
Joern Type-4 Semantic Clone Detector

This is the main interface for detecting semantic (Type-4) clones using
Joern's Program Dependence Graph (PDG) analysis.

Type-4 clones are code fragments that:
- Perform the SAME functionality
- Have DIFFERENT implementation

Examples:
- Recursive vs Iterative algorithms
- Array vs LinkedList implementations
- Different design patterns achieving same result

Supported Languages:
- Python
- Java
- JavaScript
- C
- C++
- Go
- PHP

Usage:
    from joern import JoernDetector
    
    detector = JoernDetector()
    result = detector.detect(code1, code2, language="python")
    
    if result.is_semantic_clone:
        print(f"Semantic clone found! Similarity: {result.similarity:.1%}")
"""

import logging
import time
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path

try:
    from .client import JoernClient, get_container_manager
    from .comparators import SemanticAnalyzer
    from .models import (
        PDG,
        SemanticCloneResult,
        SemanticScores,
        PDGInfo,
        ConfidenceLevel,
        BatchSemanticResult
    )
    from .config import get_config, get_semantic_config
except ImportError:
    from client import JoernClient, get_container_manager
    from comparators import SemanticAnalyzer
    from models import (
        PDG,
        SemanticCloneResult,
        SemanticScores,
        PDGInfo,
        ConfidenceLevel,
        BatchSemanticResult
    )
    from config import get_config, get_semantic_config

logger = logging.getLogger(__name__)


class JoernDetector:
    """
    Joern-based Type-4 Semantic Clone Detector
    
    Uses Program Dependence Graph (PDG) analysis to detect code clones
    that have the same functionality but different implementation.
    
    Attributes:
        config: Configuration settings
        client: Joern client for PDG extraction
        analyzer: Semantic analyzer for comparison
    
    Example:
        # Basic usage
        detector = JoernDetector()
        result = detector.detect(code1, code2, "python")
        
        if result.is_semantic_clone:
            print(f"Clone detected! Similarity: {result.similarity:.1%}")
        
        # Quick check
        if detector.is_semantic_clone(code1, code2, "java"):
            print("These are semantic clones!")
        
        # Get similarity score
        score = detector.get_similarity(code1, code2, "cpp")
        print(f"Similarity: {score:.1%}")
    """
    
    def __init__(self, auto_start: bool = True):
        """
        Initialize the Joern Detector.
        
        Args:
            auto_start: Automatically start Docker container if not running
        """
        self.config = get_config()
        self.semantic_config = get_semantic_config()
        self.client = JoernClient(auto_start=auto_start)
        self.analyzer = SemanticAnalyzer()
        
        logger.info("JoernDetector initialized for Type-4 semantic clone detection")
        logger.info(f"Supported languages: {', '.join(self.config.joern.supported_languages)}")
    
    def detect(
        self,
        code1: str,
        code2: str,
        language: str = "python"
    ) -> SemanticCloneResult:
        """
        Detect if two code snippets are semantic (Type-4) clones.
        
        This is the main detection method. It extracts PDGs from both
        code snippets and analyzes their semantic similarity.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            language: Programming language (python, java, javascript, c, cpp, go, php)
        
        Returns:
            SemanticCloneResult containing:
                - is_semantic_clone: True if codes are semantic clones
                - similarity: Overall similarity score (0.0 to 1.0)
                - confidence: Confidence level (high, medium, low)
                - scores: Detailed component scores
        
        Example:
            result = detector.detect('''
                def factorial(n):
                    if n <= 1: return 1
                    return n * factorial(n-1)
            ''', '''
                def factorial(n):
                    result = 1
                    for i in range(1, n+1):
                        result *= i
                    return result
            ''', "python")
            
            print(f"Semantic Clone: {result.is_semantic_clone}")
            print(f"Similarity: {result.similarity:.1%}")
        """
        logger.info(f"Detecting semantic clones ({language})")
        start_time = time.time()
        
        result = SemanticCloneResult(language=language)
        result.threshold_used = self.config.get_threshold_for_language(language)
        
        try:
            # Validate language
            if not self.config.is_language_supported(language):
                supported = ', '.join(self.config.joern.supported_languages)
                result.status = "error"
                result.error_message = f"Unsupported language: {language}. Supported: {supported}"
                return result
            
            # Extract PDG from first code
            logger.info("Extracting PDG from code 1...")
            pdg1 = self.client.extract_pdg_from_code(code1, language)
            
            if not pdg1:
                result.status = "error"
                result.error_message = "Failed to extract PDG from first code"
                return result
            
            result.pdg1_info = self._extract_pdg_info(pdg1)
            
            # Extract PDG from second code
            logger.info("Extracting PDG from code 2...")
            pdg2 = self.client.extract_pdg_from_code(code2, language)
            
            if not pdg2:
                result.status = "error"
                result.error_message = "Failed to extract PDG from second code"
                return result
            
            result.pdg2_info = self._extract_pdg_info(pdg2)
            
            # Analyze semantic similarity
            logger.info("Analyzing semantic similarity...")
            scores, confidence = self.analyzer.analyze(pdg1, pdg2, language)
            
            result.scores = scores
            result.similarity = scores.overall
            result.confidence = confidence
            
            # Determine if semantic clone based on threshold
            threshold = self.config.get_threshold_for_language(language)
            result.is_semantic_clone = scores.overall >= threshold
            
            result.status = "success"
            
            logger.info(
                f"Detection complete - Is Semantic Clone: {result.is_semantic_clone}, "
                f"Similarity: {result.similarity:.1%}, "
                f"Confidence: {confidence.value}"
            )
            
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            result.status = "error"
            result.error_message = str(e)
        
        finally:
            self.client.cleanup()
            result.analysis_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def detect_from_files(
        self,
        file1_path: str,
        file2_path: str
    ) -> SemanticCloneResult:
        """
        Detect semantic clones between two source files.
        
        Language is automatically detected from file extension.
        
        Args:
            file1_path: Path to first source file
            file2_path: Path to second source file
        
        Returns:
            SemanticCloneResult
        
        Example:
            result = detector.detect_from_files("utils.py", "helpers.py")
        """
        logger.info(f"Detecting semantic clones: {file1_path} vs {file2_path}")
        
        try:
            path1 = Path(file1_path)
            path2 = Path(file2_path)
            
            if not path1.exists():
                result = SemanticCloneResult(status="error")
                result.error_message = f"File not found: {file1_path}"
                return result
            
            if not path2.exists():
                result = SemanticCloneResult(status="error")
                result.error_message = f"File not found: {file2_path}"
                return result
            
            code1 = path1.read_text()
            code2 = path2.read_text()
            
            # Auto-detect language from extension
            language = self.config.get_language_from_extension(file1_path) or "python"
            
            # Run detection
            result = self.detect(code1, code2, language)
            result.code1_path = str(file1_path)
            result.code2_path = str(file2_path)
            
            return result
            
        except Exception as e:
            result = SemanticCloneResult(status="error")
            result.error_message = str(e)
            return result
    
    def is_semantic_clone(
        self,
        code1: str,
        code2: str,
        language: str = "python"
    ) -> bool:
        """
        Quick check if two code snippets are semantic clones.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            language: Programming language
        
        Returns:
            True if semantic clones, False otherwise
        
        Example:
            if detector.is_semantic_clone(recursive_code, iterative_code, "python"):
                print("These implementations are semantic clones!")
        """
        result = self.detect(code1, code2, language)
        return result.is_semantic_clone
    
    def get_similarity(
        self,
        code1: str,
        code2: str,
        language: str = "python"
    ) -> float:
        """
        Get semantic similarity score between two code snippets.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            language: Programming language
        
        Returns:
            Similarity score from 0.0 (completely different) to 1.0 (identical)
        
        Example:
            score = detector.get_similarity(code1, code2, "java")
            print(f"These codes are {score:.1%} similar semantically")
        """
        result = self.detect(code1, code2, language)
        return result.similarity if result.status == "success" else 0.0
    
    def detect_batch(
        self,
        code_pairs: List[Tuple[str, str]],
        language: str = "python"
    ) -> BatchSemanticResult:
        """
        Detect semantic clones for multiple code pairs.
        
        Args:
            code_pairs: List of (code1, code2) tuples
            language: Programming language (same for all pairs)
        
        Returns:
            BatchSemanticResult with all results
        
        Example:
            pairs = [(code1a, code1b), (code2a, code2b), (code3a, code3b)]
            batch_result = detector.detect_batch(pairs, "python")
            print(f"Found {batch_result.semantic_clones_found} clones")
        """
        logger.info(f"Batch detection for {len(code_pairs)} pairs")
        start_time = time.time()
        
        batch_result = BatchSemanticResult()
        
        for i, (code1, code2) in enumerate(code_pairs):
            logger.info(f"Processing pair {i + 1}/{len(code_pairs)}")
            result = self.detect(code1, code2, language)
            batch_result.add_result(result)
        
        batch_result.total_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Batch complete: {batch_result.semantic_clones_found}/{batch_result.total_comparisons} "
            f"semantic clones found"
        )
        
        return batch_result
    
    def detect_in_directory(
        self,
        directory: str,
        extensions: List[str] = None
    ) -> BatchSemanticResult:
        """
        Find all semantic clone pairs in a directory.
        
        Compares all files with matching extensions against each other.
        
        Args:
            directory: Path to directory
            extensions: File extensions to include (default: [".py"])
        
        Returns:
            BatchSemanticResult with all clone pairs found
        
        Example:
            result = detector.detect_in_directory("./src", [".py", ".java"])
            for clone in result.results:
                if clone.is_semantic_clone:
                    print(f"{clone.code1_path} <-> {clone.code2_path}")
        """
        extensions = extensions or [".py"]
        directory = Path(directory)
        
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return BatchSemanticResult()
        
        # Find all matching files
        files = []
        for ext in extensions:
            files.extend(directory.glob(f"**/*{ext}"))
        
        files = list(files)
        logger.info(f"Found {len(files)} files in {directory}")
        
        if len(files) < 2:
            logger.warning("Need at least 2 files to compare")
            return BatchSemanticResult()
        
        # Compare all pairs
        batch_result = BatchSemanticResult()
        total_pairs = len(files) * (len(files) - 1) // 2
        current_pair = 0
        
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                current_pair += 1
                logger.info(f"Comparing pair {current_pair}/{total_pairs}")
                
                result = self.detect_from_files(str(files[i]), str(files[j]))
                batch_result.add_result(result)
        
        return batch_result
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.
        
        Returns:
            List of language names
        """
        return self.config.joern.supported_languages.copy()
    
    def get_threshold(self, language: str = "python") -> float:
        """
        Get detection threshold for a specific language.
        
        Args:
            language: Programming language
        
        Returns:
            Threshold value (0.0 to 1.0)
        """
        return self.config.get_threshold_for_language(language)
    
    def set_threshold(self, threshold: float, language: str = None):
        """
        Set detection threshold.
        
        Args:
            threshold: New threshold value (0.0 to 1.0)
            language: If provided, set language-specific threshold
        """
        if language:
            base = self.semantic_config.semantic_clone_threshold
            adjustment = threshold - base
            self.semantic_config.language_threshold_adjustments[language] = adjustment
        else:
            self.semantic_config.semantic_clone_threshold = threshold
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get detector status information.
        
        Returns:
            Dictionary with status information
        """
        container_manager = get_container_manager()
        info = container_manager.get_container_info()
        
        return {
            "docker_available": info["docker_available"],
            "container_running": info["running"],
            "container_name": info.get("name", ""),
            "supported_languages": self.get_supported_languages(),
            "default_threshold": self.semantic_config.semantic_clone_threshold,
            "language_thresholds": {
                lang: self.get_threshold(lang) 
                for lang in self.config.joern.supported_languages
            }
        }
    
    def start_container(self) -> bool:
        """
        Start the Joern Docker container.
        
        Returns:
            True if started successfully
        """
        return self.client.ensure_container_running()
    
    def stop_container(self) -> bool:
        """
        Stop the Joern Docker container.
        
        Returns:
            True if stopped successfully
        """
        container_manager = get_container_manager()
        return container_manager.stop_container()
    
    def _extract_pdg_info(self, pdg: PDG) -> PDGInfo:
        """Extract information from PDG for result"""
        return PDGInfo(
            num_methods=len(pdg.methods),
            num_nodes=pdg.total_nodes,
            num_edges=pdg.total_edges,
            num_control_edges=pdg.total_control_edges,
            num_data_edges=pdg.total_data_edges,
            method_names=[m.method_name for m in pdg.methods]
        )
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.client.cleanup()
    
    def __repr__(self):
        """String representation"""
        status = self.get_status()
        return (
            f"JoernDetector("
            f"running={status['container_running']}, "
            f"languages={len(status['supported_languages'])}, "
            f"threshold={status['default_threshold']:.0%})"
        )


# Convenience function for easy access
def get_joern_detector(auto_start: bool = True) -> JoernDetector:
    """
    Get a JoernDetector instance.
    
    Args:
        auto_start: Automatically start Docker container if not running
    
    Returns:
        JoernDetector instance
    
    Example:
        detector = get_joern_detector()
        result = detector.detect(code1, code2, "python")
    """
    return JoernDetector(auto_start=auto_start)