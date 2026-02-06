# analysis-engine/detectors/type4/similarity.py

"""
PDG Similarity Calculator for Type-4 Clone Detection

Calculates overall semantic similarity from pairwise feature comparisons.
Uses weighted combination of different feature categories.
"""

from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class SimilarityWeights:
    """
    Weights for each feature category in the final score.
    
    These weights determine how much each category contributes to
    the overall semantic similarity score.
    """
    control_flow: float = 0.25      # How the code flows (loops, conditions)
    data_flow: float = 0.25         # How data moves between statements
    call_pattern: float = 0.20      # What functions are called
    structural: float = 0.15        # Shape of the code
    behavioral: float = 0.15        # Overall behavior signature
    
    def validate(self) -> bool:
        """Check that weights sum to 1.0"""
        total = (
            self.control_flow + self.data_flow + 
            self.call_pattern + self.structural + self.behavioral
        )
        return abs(total - 1.0) < 0.001


class PDGSimilarity:
    """
    Calculates semantic similarity between two PDGs.
    
    Uses a weighted combination of category scores:
    - Control Flow: Loop patterns, conditions, nesting
    - Data Flow: Variables, dependencies
    - Call Pattern: Function calls
    - Structural: Nodes, edges
    - Behavioral: Hash similarity
    """
    
    # Default weights
    DEFAULT_WEIGHTS = SimilarityWeights()
    
    # Confidence thresholds
    THRESHOLDS = {
        'HIGH': 0.80,
        'MEDIUM': 0.60,
        'LOW': 0.40,
    }
    
    def __init__(self, weights: SimilarityWeights = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        
        if not self.weights.validate():
            raise ValueError("Weights must sum to 1.0")
    
    def calculate_similarity(
        self,
        pair_features: Dict[str, float]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate overall semantic similarity from pair features.
        
        Args:
            pair_features: Dictionary of similarity scores from SemanticFeatureExtractor
            
        Returns:
            Tuple of (overall_score, category_scores)
        """
        
        # === Calculate Control Flow Score ===
        control_flow_score = self._calculate_control_flow_score(pair_features)
        
        # === Calculate Data Flow Score ===
        data_flow_score = self._calculate_data_flow_score(pair_features)
        
        # === Calculate Call Pattern Score ===
        call_pattern_score = self._calculate_call_pattern_score(pair_features)
        
        # === Calculate Structural Score ===
        structural_score = self._calculate_structural_score(pair_features)
        
        # === Calculate Behavioral Score ===
        behavioral_score = self._calculate_behavioral_score(pair_features)
        
        # === Weighted Combination ===
        overall = (
            control_flow_score * self.weights.control_flow +
            data_flow_score * self.weights.data_flow +
            call_pattern_score * self.weights.call_pattern +
            structural_score * self.weights.structural +
            behavioral_score * self.weights.behavioral
        )
        
        category_scores = {
            'control_flow': round(control_flow_score, 4),
            'data_flow': round(data_flow_score, 4),
            'call_pattern': round(call_pattern_score, 4),
            'structural': round(structural_score, 4),
            'behavioral': round(behavioral_score, 4),
        }
        
        return round(overall, 4), category_scores
    
    def _calculate_control_flow_score(self, pf: Dict[str, float]) -> float:
        """
        Calculate control flow category score.
        
        Considers:
        - Loop similarity (how similar are loop patterns)
        - Condition similarity (how similar are condition patterns)
        - Nesting similarity (how similar is nesting depth)
        - Recursion match (do both use recursion or not)
        - Control signature similarity (pattern of control structures)
        """
        return (
            pf.get('loop_similarity', 0) * 0.25 +
            pf.get('condition_similarity', 0) * 0.25 +
            pf.get('nesting_similarity', 0) * 0.15 +
            pf.get('recursion_match', 0) * 0.20 +
            pf.get('control_signature_similarity', 0) * 0.15
        )
    
    def _calculate_data_flow_score(self, pf: Dict[str, float]) -> float:
        """
        Calculate data flow category score.
        
        Considers:
        - Variable similarity (how many variables)
        - Dependency similarity (how many data dependencies)
        - Def/use ratio similarity (pattern of variable usage)
        """
        return (
            pf.get('variable_similarity', 0) * 0.40 +
            pf.get('dependency_similarity', 0) * 0.40 +
            pf.get('def_use_similarity', 0) * 0.20
        )
    
    def _calculate_call_pattern_score(self, pf: Dict[str, float]) -> float:
        """
        Calculate call pattern category score.
        
        Considers:
        - Call count similarity (total calls)
        - Unique call similarity (unique functions called)
        - Call overlap (which functions are called)
        """
        return (
            pf.get('call_count_similarity', 0) * 0.30 +
            pf.get('unique_call_similarity', 0) * 0.30 +
            pf.get('call_overlap_similarity', 0) * 0.40
        )
    
    def _calculate_structural_score(self, pf: Dict[str, float]) -> float:
        """
        Calculate structural category score.
        
        Considers:
        - Node similarity (PDG size)
        - Edge similarity (PDG connectivity)
        - Return similarity (return statement pattern)
        """
        return (
            pf.get('node_similarity', 0) * 0.40 +
            pf.get('edge_similarity', 0) * 0.40 +
            pf.get('return_similarity', 0) * 0.20
        )
    
    def _calculate_behavioral_score(self, pf: Dict[str, float]) -> float:
        """
        Calculate behavioral category score.
        
        Considers:
        - Behavioral hash similarity (overall bucket matching)
        - Individual bucket matches
        """
        # Primary: behavioral hash similarity (compares all buckets at once)
        hash_sim = pf.get('behavioral_hash_similarity', 0)
        
        # Secondary: individual bucket matches (for finer granularity)
        iteration_match = pf.get('iteration_bucket_match', 0)
        complexity_match = pf.get('complexity_bucket_match', 0)
        nesting_match = pf.get('nesting_bucket_match', 0)
        data_match = pf.get('data_bucket_match', 0)
        call_match = pf.get('call_bucket_match', 0)
        return_match = pf.get('return_bucket_match', 0)
        
        # Weighted combination
        # Give more weight to iteration pattern (LOOP vs REC vs DIRECT)
        individual_score = (
            iteration_match * 0.30 +      # Most important: how does it iterate?
            complexity_match * 0.20 +
            nesting_match * 0.15 +
            data_match * 0.15 +
            call_match * 0.10 +
            return_match * 0.10
        )
        
        # Combine hash similarity with individual scores
        return hash_sim * 0.60 + individual_score * 0.40
    
    def get_confidence_level(self, score: float) -> str:
        """
        Determine confidence level based on semantic similarity score.
        
        Args:
            score: Semantic similarity score (0.0 to 1.0)
            
        Returns:
            Confidence level: 'HIGH', 'MEDIUM', 'LOW', or 'UNLIKELY'
        """
        if score >= self.THRESHOLDS['HIGH']:
            return 'HIGH'
        elif score >= self.THRESHOLDS['MEDIUM']:
            return 'MEDIUM'
        elif score >= self.THRESHOLDS['LOW']:
            return 'LOW'
        else:
            return 'UNLIKELY'
    
    def get_detailed_analysis(
        self,
        pair_features: Dict[str, float],
        overall_score: float,
        category_scores: Dict[str, float]
    ) -> Dict:
        """
        Get detailed analysis of similarity results.
        
        Provides human-readable insights about why two codes are similar or different.
        """
        analysis = {
            'overall_score': overall_score,
            'confidence': self.get_confidence_level(overall_score),
            'category_scores': category_scores,
            'insights': [],
            'differences': [],
        }
        
        # Analyze control flow
        if category_scores['control_flow'] >= 0.8:
            analysis['insights'].append("Very similar control flow patterns")
        elif category_scores['control_flow'] < 0.4:
            analysis['differences'].append("Different control flow structures")
        
        # Analyze recursion
        if pair_features.get('recursion_match', 0) == 0:
            analysis['differences'].append("One uses recursion, the other doesn't")
        
        # Analyze iteration pattern
        if pair_features.get('iteration_bucket_match', 0) == 0:
            analysis['differences'].append("Different iteration approaches (loop vs recursion vs direct)")
        elif pair_features.get('iteration_bucket_match', 0) == 1:
            analysis['insights'].append("Same iteration approach")
        
        # Analyze data flow
        if category_scores['data_flow'] >= 0.8:
            analysis['insights'].append("Similar data flow patterns")
        elif category_scores['data_flow'] < 0.4:
            analysis['differences'].append("Different variable usage patterns")
        
        # Analyze call patterns
        if category_scores['call_pattern'] >= 0.8:
            analysis['insights'].append("Similar function call patterns")
        elif category_scores['call_pattern'] < 0.4:
            analysis['differences'].append("Different functions called")
        
        # Analyze behavioral hash
        behavioral_sim = pair_features.get('behavioral_hash_similarity', 0)
        if behavioral_sim >= 0.8:
            analysis['insights'].append("Very similar behavioral signature")
        elif behavioral_sim >= 0.5:
            analysis['insights'].append("Moderately similar behavior")
        else:
            analysis['differences'].append("Different behavioral patterns")
        
        # Overall assessment
        if overall_score >= 0.75:
            analysis['assessment'] = "Highly likely to be semantic clones (same functionality)"
        elif overall_score >= 0.60:
            analysis['assessment'] = "Possibly semantic clones, manual review recommended"
        elif overall_score >= 0.40:
            analysis['assessment'] = "Some similarities but likely different implementations"
        else:
            analysis['assessment'] = "Unlikely to be related implementations"
        
        return analysis


class SimilarityResult:
    """
    Wrapper class for similarity calculation results.
    
    Provides convenient access to all similarity information.
    """
    
    def __init__(
        self,
        overall_score: float,
        category_scores: Dict[str, float],
        pair_features: Dict[str, float],
        confidence: str
    ):
        self.overall_score = overall_score
        self.category_scores = category_scores
        self.pair_features = pair_features
        self.confidence = confidence
    
    @property
    def is_semantic_clone(self) -> bool:
        """Check if this is likely a semantic clone (score >= 0.60)"""
        return self.overall_score >= 0.60
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high confidence detection"""
        return self.confidence == 'HIGH'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'overall_score': self.overall_score,
            'is_semantic_clone': self.is_semantic_clone,
            'confidence': self.confidence,
            'category_scores': self.category_scores,
        }
    
    def __repr__(self) -> str:
        return (
            f"SimilarityResult(score={self.overall_score:.4f}, "
            f"confidence={self.confidence}, is_clone={self.is_semantic_clone})"
        )