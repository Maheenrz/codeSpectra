# detectors/type4/joern/metrics/similarity_metrics.py

"""
Multi-Metric Similarity Computation for Type-4 Clone Detection

Implements 5 different similarity metrics optimized for semantic comparison.
Research basis: SEED, Dual-GCN, BigCloneBench methodologies
"""

from collections import Counter
from typing import Dict, List, Set, Tuple
import numpy as np
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class SimilarityMetrics:
    """
    Compute multiple similarity metrics between extracted features
    """
    
    def __init__(self):
        # Weights for combining metrics (from research)
        self.default_weights = {
            'ast_similarity': 0.15,
            'control_flow_similarity': 0.35,
            'data_flow_similarity': 0.30,
            'api_similarity': 0.15,
            'signature_similarity': 0.05
        }
    
    def compute_all_similarities(
        self,
        features1: Dict,
        features2: Dict
    ) -> Dict[str, float]:
        """
        Compute all similarity metrics
        
        Args:
            features1: Features from first code
            features2: Features from second code
            
        Returns:
            Dictionary of similarity scores (0.0 to 1.0)
        """
        return {
            'ast_similarity': self.compute_ast_similarity(
                features1['ast_features'],
                features2['ast_features']
            ),
            'control_flow_similarity': self.compute_control_flow_similarity(
                features1['control_flow'],
                features2['control_flow']
            ),
            'data_flow_similarity': self.compute_data_flow_similarity(
                features1['data_flow'],
                features2['data_flow']
            ),
            'api_similarity': self.compute_api_similarity(
                features1['api_calls'],
                features2['api_calls']
            ),
            'signature_similarity': self.compute_signature_similarity(
                features1['semantic_sig'],
                features2['semantic_sig']
            ),
            'operator_similarity': self.compute_operator_similarity(
                features1.get('operators', Counter()),
                features2.get('operators', Counter())
            ),
            'structural_similarity': self.compute_structural_similarity(
                features1.get('structure', {}),
                features2.get('structure', {})
            )
        }
    
    def compute_weighted_similarity(
        self,
        similarities: Dict[str, float],
        weights: Dict[str, float] = None
    ) -> float:
        """
        Compute weighted average similarity
        
        Args:
            similarities: Dictionary of similarity scores
            weights: Optional custom weights
            
        Returns:
            Weighted similarity score (0.0 to 1.0)
        """
        weights = weights or self.default_weights
        
        # Filter similarities to only those with weights
        weighted_sum = sum(
            similarities.get(key, 0.0) * weight
            for key, weight in weights.items()
            if key in similarities
        )
        
        total_weight = sum(weights.values())
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def compute_ast_similarity(
        self,
        ast1: Counter,
        ast2: Counter
    ) -> float:
        """
        Compute AST node type distribution similarity
        Uses cosine similarity
        """
        return self.cosine_similarity(ast1, ast2)
    
    def compute_control_flow_similarity(
        self,
        cf1: Dict,
        cf2: Dict
    ) -> float:
        """
        Compute control flow similarity
        Combines sequence similarity and pattern similarity
        """
        # Sequence similarity (LCS-based)
        seq1 = cf1.get('sequence', [])
        seq2 = cf2.get('sequence', [])
        seq_sim = self.sequence_similarity(seq1, seq2)
        
        # Pattern similarity (Jaccard)
        patterns1 = set(cf1.get('patterns', Counter()).keys())
        patterns2 = set(cf2.get('patterns', Counter()).keys())
        pattern_sim = self.jaccard_similarity(patterns1, patterns2)
        
        # Structural metrics similarity
        metrics = ['num_branches', 'num_loops', 'nesting_depth']
        metric_sims = []
        
        for metric in metrics:
            v1 = cf1.get(metric, 0)
            v2 = cf2.get(metric, 0)
            
            if v1 == 0 and v2 == 0:
                metric_sims.append(1.0)
            else:
                # Relative similarity
                metric_sims.append(1.0 - abs(v1 - v2) / (max(v1, v2) + 1e-10))
        
        struct_sim = np.mean(metric_sims) if metric_sims else 0.0
        
        # Combine: 50% sequence, 30% patterns, 20% structure
        return 0.5 * seq_sim + 0.3 * pattern_sim + 0.2 * struct_sim
    
    def compute_data_flow_similarity(
        self,
        df1: Dict,
        df2: Dict
    ) -> float:
        """
        Compute data flow pattern similarity
        Uses Jaccard similarity on abstracted patterns
        """
        patterns1 = df1.get('patterns', set())
        patterns2 = df2.get('patterns', set())
        
        # Jaccard similarity of patterns
        jaccard = self.jaccard_similarity(patterns1, patterns2)
        
        # Variable count similarity
        v1 = df1.get('num_variables', 0)
        v2 = df2.get('num_variables', 0)
        
        var_sim = (
            1.0 - abs(v1 - v2) / (max(v1, v2) + 1e-10)
            if (v1 > 0 or v2 > 0) else 1.0
        )
        
        # Combine: 70% patterns, 30% variables
        return 0.7 * jaccard + 0.3 * var_sim
    
    def compute_api_similarity(
        self,
        api1: Dict,
        api2: Dict
    ) -> float:
        """
        Compute API call sequence similarity
        Uses LCS for sequence + Jaccard for unique APIs
        """
        seq1 = api1.get('sequence', [])
        seq2 = api2.get('sequence', [])
        
        # LCS similarity for sequence
        seq_sim = self.lcs_similarity(seq1, seq2)
        
        # Jaccard similarity for unique APIs
        unique1 = set(seq1)
        unique2 = set(seq2)
        jaccard = self.jaccard_similarity(unique1, unique2)
        
        # API pattern similarity
        patterns1 = set(api1.get('patterns', []))
        patterns2 = set(api2.get('patterns', []))
        pattern_sim = self.jaccard_similarity(patterns1, patterns2)
        
        # Combine: 40% sequence, 30% unique APIs, 30% patterns
        return 0.4 * seq_sim + 0.3 * jaccard + 0.3 * pattern_sim
    
    def compute_signature_similarity(
        self,
        sig1: Set[str],
        sig2: Set[str]
    ) -> float:
        """
        Compute semantic signature similarity
        Uses Jaccard similarity
        """
        return self.jaccard_similarity(sig1, sig2)
    
    def compute_operator_similarity(
        self,
        op1: Counter,
        op2: Counter
    ) -> float:
        """
        Compute operator usage similarity
        Uses cosine similarity
        """
        return self.cosine_similarity(op1, op2)
    
    def compute_structural_similarity(
        self,
        struct1: Dict,
        struct2: Dict
    ) -> float:
        """
        Compute overall structural similarity
        """
        metrics = [
            'num_methods',
            'num_nodes',
            'num_edges',
            'control_data_ratio'
        ]
        
        sims = []
        for metric in metrics:
            v1 = struct1.get(metric, 0)
            v2 = struct2.get(metric, 0)
            
            if v1 == 0 and v2 == 0:
                sims.append(1.0)
            elif metric == 'control_data_ratio':
                # For ratios, use direct difference
                sims.append(1.0 - abs(v1 - v2))
            else:
                # For counts, use relative similarity
                sims.append(1.0 - abs(v1 - v2) / (max(v1, v2) + 1e-10))
        
        return np.mean(sims) if sims else 0.0
    
    # Core similarity functions
    
    @staticmethod
    def cosine_similarity(counter1: Counter, counter2: Counter) -> float:
        """
        Compute cosine similarity between two Counters
        """
        all_keys = set(counter1.keys()) | set(counter2.keys())
        
        if not all_keys:
            return 1.0
        
        # Build vectors
        vec1 = np.array([counter1.get(k, 0) for k in all_keys], dtype=float)
        vec2 = np.array([counter2.get(k, 0) for k in all_keys], dtype=float)
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def jaccard_similarity(set1: Set, set2: Set) -> float:
        """
        Compute Jaccard similarity between two sets
        """
        if not set1 and not set2:
            return 1.0
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def sequence_similarity(seq1: List, seq2: List) -> float:
        """
        Compute sequence similarity using SequenceMatcher
        """
        if not seq1 and not seq2:
            return 1.0
        
        if not seq1 or not seq2:
            return 0.0
        
        matcher = SequenceMatcher(None, seq1, seq2)
        return matcher.ratio()
    
    @staticmethod
    def lcs_similarity(seq1: List, seq2: List) -> float:
        """
        Compute LCS-based similarity
        """
        if not seq1 and not seq2:
            return 1.0
        
        if not seq1 or not seq2:
            return 0.0
        
        # Compute LCS length
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs_length = dp[m][n]
        max_length = max(len(seq1), len(seq2))
        
        return lcs_length / max_length if max_length > 0 else 0.0


def get_similarity_metrics() -> SimilarityMetrics:
    """Get SimilarityMetrics instance"""
    return SimilarityMetrics()