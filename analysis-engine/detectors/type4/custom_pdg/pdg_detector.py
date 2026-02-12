# analysis-engine/detectors/type4/pdg_detector.py

"""
Type-4 Semantic Clone Detector using Simplified PDG

This is the main detector class that orchestrates:
1. PDG building from source files
2. Semantic feature extraction
3. Similarity calculation
4. Result generation

Usage:
    detector = Type4PDGDetector(threshold=0.60)
    result = detector.detect("file_a.cpp", "file_b.cpp")
    
    # Or for batch detection:
    results = detector.detect_batch(["file1.cpp", "file2.cpp", "file3.cpp"])
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
import time

from .pdg_builder import PDGBuilder, SimplifiedPDG
from .semantic_features import SemanticFeatureExtractor, SemanticFeatures
from .similarity import PDGSimilarity, SimilarityResult, SimilarityWeights


# =============================================================================
# RESULT DATA STRUCTURES
# =============================================================================

@dataclass
class Type4DetectionResult:
    """
    Result of Type-4 clone detection between two files.
    """
    file_a: str
    file_b: str
    
    # Main results
    semantic_score: float
    is_semantic_clone: bool
    confidence: str
    
    # Category breakdown
    category_scores: Dict[str, float]
    
    # Features (for debugging/analysis)
    features_a: Dict[str, Any] = field(default_factory=dict)
    features_b: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'file_a': self.file_a,
            'file_b': self.file_b,
            'semantic_score': self.semantic_score,
            'is_semantic_clone': self.is_semantic_clone,
            'confidence': self.confidence,
            'category_scores': self.category_scores,
            'features_a': self.features_a,
            'features_b': self.features_b,
            'processing_time_ms': self.processing_time_ms,
        }


@dataclass
class Type4BatchResult:
    """
    Result of batch Type-4 clone detection.
    """
    total_files: int
    total_comparisons: int
    clone_pairs: int
    suspicious_pairs: int
    processing_time_ms: float
    
    confidence_breakdown: Dict[str, int] = field(default_factory=dict)
    results: List[Type4DetectionResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_files': self.total_files,
            'total_comparisons': self.total_comparisons,
            'clone_pairs': self.clone_pairs,
            'suspicious_pairs': self.suspicious_pairs,
            'processing_time_ms': self.processing_time_ms,
            'confidence_breakdown': self.confidence_breakdown,
            'results': [r.to_dict() for r in self.results],
        }
    
    def get_high_confidence_clones(self) -> List[Type4DetectionResult]:
        """Get only HIGH confidence clone pairs"""
        return [r for r in self.results if r.confidence == 'HIGH']
    
    def get_clones(self) -> List[Type4DetectionResult]:
        """Get all clone pairs (is_semantic_clone = True)"""
        return [r for r in self.results if r.is_semantic_clone]


# =============================================================================
# TYPE-4 PDG DETECTOR
# =============================================================================

class Type4PDGDetector:
    """
    Type-4 Semantic Clone Detector using Program Dependence Graph analysis.
    
    Detects code that has:
    - Different syntax
    - Different algorithms  
    - But SAME semantic behavior (produce same output)
    
    Example:
        # Iterative sum
        for(i=1; i<=n; i++) total += i;
        
        # Formula sum (SEMANTIC CLONE - different code, same result!)
        return n * (n + 1) / 2;
        
        # Recursive sum (SEMANTIC CLONE - different code, same result!)
        if(n <= 0) return 0; return n + sum(n-1);
    
    Usage:
        detector = Type4PDGDetector(threshold=0.60)
        result = detector.detect("file_a.cpp", "file_b.cpp")
    """
    
    # Default threshold for semantic clone detection
    DEFAULT_THRESHOLD = 0.60
    
    def __init__(
        self, 
        threshold: float = DEFAULT_THRESHOLD,
        weights: SimilarityWeights = None
    ):
        """
        Initialize the Type-4 detector.
        
        Args:
            threshold: Minimum semantic score to be considered a clone (default: 0.60)
            weights: Custom weights for similarity calculation (optional)
        """
        self.threshold = threshold
        
        # Initialize components
        self.pdg_builder = PDGBuilder()
        self.feature_extractor = SemanticFeatureExtractor()
        self.similarity_calculator = PDGSimilarity(weights=weights)
        
        # Caches for performance
        self._pdg_cache: Dict[str, SimplifiedPDG] = {}
        self._feature_cache: Dict[str, SemanticFeatures] = {}
        
        print(f"✅ Type-4 PDG Detector initialized (threshold: {threshold})")
    
    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    
    def detect(
        self, 
        file_path_a: str, 
        file_path_b: str,
        include_features: bool = True
    ) -> Dict[str, Any]:
        """
        Detect Type-4 semantic clones between two files.
        
        Args:
            file_path_a: Path to first source file
            file_path_b: Path to second source file
            include_features: Whether to include detailed features in result
            
        Returns:
            Dictionary containing detection results
        """
        start_time = time.time()
        
        # Build PDGs (from cache if available)
        pdg_a = self._get_pdg(file_path_a)
        pdg_b = self._get_pdg(file_path_b)
        
        # Extract features (from cache if available)
        feat_a = self._get_features(file_path_a, pdg_a)
        feat_b = self._get_features(file_path_b, pdg_b)
        
        # Compute pairwise features
        pair_features = self.feature_extractor.compute_pair_features(feat_a, feat_b)
        
        # Calculate similarity
        semantic_score, category_scores = self.similarity_calculator.calculate_similarity(
            pair_features
        )
        
        # Determine results
        is_clone = semantic_score >= self.threshold
        confidence = self.similarity_calculator.get_confidence_level(semantic_score)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Build result
        result = {
            'file_a': Path(file_path_a).name,
            'file_b': Path(file_path_b).name,
            'semantic_score': semantic_score,
            'is_semantic_clone': is_clone,
            'confidence': confidence,
            'threshold_used': self.threshold,
            'category_scores': category_scores,
            'processing_time_ms': round(processing_time, 2),
        }
        
        # Include detailed features if requested
        if include_features:
            result['features_a'] = self.feature_extractor.to_dict(feat_a)
            result['features_b'] = self.feature_extractor.to_dict(feat_b)
            result['pair_features'] = pair_features
        
        return result
    
    def detect_batch(
        self, 
        file_paths: List[str],
        include_unlikely: bool = False
    ) -> Type4BatchResult:
        """
        Detect Type-4 clones among multiple files.
        
        Compares all pairs of files and returns results sorted by semantic score.
        
        Args:
            file_paths: List of file paths to compare
            include_unlikely: Whether to include UNLIKELY confidence pairs
            
        Returns:
            Type4BatchResult containing all detection results
        """
        start_time = time.time()
        
        # Clear caches for fresh batch
        self.clear_cache()
        
        results: List[Type4DetectionResult] = []
        n = len(file_paths)
        total_comparisons = (n * (n - 1)) // 2
        
        print(f"🔍 Comparing {n} files ({total_comparisons} pairs)...")
        
        # Compare all pairs
        for i in range(n):
            for j in range(i + 1, n):
                detection = self.detect(
                    file_paths[i], 
                    file_paths[j],
                    include_features=False  # Don't include for batch (too much data)
                )
                
                # Filter based on confidence
                confidence = detection['confidence']
                if include_unlikely or confidence != 'UNLIKELY':
                    result = Type4DetectionResult(
                        file_a=detection['file_a'],
                        file_b=detection['file_b'],
                        semantic_score=detection['semantic_score'],
                        is_semantic_clone=detection['is_semantic_clone'],
                        confidence=confidence,
                        category_scores=detection['category_scores'],
                        processing_time_ms=detection['processing_time_ms'],
                    )
                    results.append(result)
        
        # Sort by semantic score (highest first)
        results.sort(key=lambda x: x.semantic_score, reverse=True)
        
        # Calculate statistics
        clone_pairs = sum(1 for r in results if r.is_semantic_clone)
        
        confidence_breakdown = {
            'HIGH': sum(1 for r in results if r.confidence == 'HIGH'),
            'MEDIUM': sum(1 for r in results if r.confidence == 'MEDIUM'),
            'LOW': sum(1 for r in results if r.confidence == 'LOW'),
        }
        if include_unlikely:
            confidence_breakdown['UNLIKELY'] = sum(
                1 for r in results if r.confidence == 'UNLIKELY'
            )
        
        total_time = (time.time() - start_time) * 1000
        
        return Type4BatchResult(
            total_files=n,
            total_comparisons=total_comparisons,
            clone_pairs=clone_pairs,
            suspicious_pairs=len(results),
            processing_time_ms=round(total_time, 2),
            confidence_breakdown=confidence_breakdown,
            results=results,
        )
    
    def analyze_pair(
        self,
        file_path_a: str,
        file_path_b: str
    ) -> Dict[str, Any]:
        """
        Get detailed analysis of a pair of files.
        
        Provides human-readable insights about why codes are similar or different.
        
        Args:
            file_path_a: Path to first file
            file_path_b: Path to second file
            
        Returns:
            Detailed analysis dictionary
        """
        # Get basic detection
        detection = self.detect(file_path_a, file_path_b, include_features=True)
        
        # Get detailed analysis
        analysis = self.similarity_calculator.get_detailed_analysis(
            detection['pair_features'],
            detection['semantic_score'],
            detection['category_scores']
        )
        
        # Combine results
        return {
            **detection,
            'analysis': analysis,
        }
    
    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================
    
    def _get_pdg(self, file_path: str) -> SimplifiedPDG:
        """Get PDG from cache or build it"""
        if file_path not in self._pdg_cache:
            self._pdg_cache[file_path] = self.pdg_builder.build_from_file(file_path)
        return self._pdg_cache[file_path]
    
    def _get_features(
        self, 
        file_path: str, 
        pdg: SimplifiedPDG = None
    ) -> SemanticFeatures:
        """Get features from cache or extract them"""
        if file_path not in self._feature_cache:
            if pdg is None:
                pdg = self._get_pdg(file_path)
            self._feature_cache[file_path] = self.feature_extractor.extract(pdg)
        return self._feature_cache[file_path]
    
    def clear_cache(self):
        """Clear PDG and feature caches"""
        self._pdg_cache.clear()
        self._feature_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'pdg_cache_size': len(self._pdg_cache),
            'feature_cache_size': len(self._feature_cache),
        }
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_clone_type(self) -> str:
        """Return the clone type this detector handles"""
        return "type4"
    
    def get_config(self) -> Dict[str, Any]:
        """Get detector configuration"""
        return {
            'clone_type': 'type4',
            'method': 'PDG (Program Dependence Graph)',
            'threshold': self.threshold,
            'weights': {
                'control_flow': self.similarity_calculator.weights.control_flow,
                'data_flow': self.similarity_calculator.weights.data_flow,
                'call_pattern': self.similarity_calculator.weights.call_pattern,
                'structural': self.similarity_calculator.weights.structural,
                'behavioral': self.similarity_calculator.weights.behavioral,
            },
            'confidence_levels': self.similarity_calculator.THRESHOLDS,
        }


# =============================================================================
# RESULT WRAPPER (for compatibility)
# =============================================================================

class Type4ResultWrapper:
    """
    Wrapper for batch detection results.
    Provides convenient access methods.
    """
    
    def __init__(self, batch_result: Type4BatchResult):
        self.batch_result = batch_result
        self.results = batch_result.results
        self.clone_count = batch_result.clone_pairs
        self.suspicious_count = batch_result.suspicious_pairs
    
    def get_high_confidence(self) -> List[Type4DetectionResult]:
        """Get HIGH confidence results"""
        return [r for r in self.results if r.confidence == 'HIGH']
    
    def get_medium_confidence(self) -> List[Type4DetectionResult]:
        """Get MEDIUM confidence results"""
        return [r for r in self.results if r.confidence == 'MEDIUM']
    
    def get_low_confidence(self) -> List[Type4DetectionResult]:
        """Get LOW confidence results"""
        return [r for r in self.results if r.confidence == 'LOW']
    
    def get_clones_only(self) -> List[Type4DetectionResult]:
        """Get only actual clones (is_semantic_clone = True)"""
        return [r for r in self.results if r.is_semantic_clone]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return self.batch_result.to_dict()
    
    def __len__(self) -> int:
        return len(self.results)
    
    def __iter__(self):
        return iter(self.results)