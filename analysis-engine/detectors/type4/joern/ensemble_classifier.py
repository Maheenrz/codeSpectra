# detectors/type4/joern/classifiers/ensemble_classifier.py

"""
Ensemble Classifier for Type-4 Clone Detection

Combines multiple similarity metrics with:
1. Weighted averaging
2. Adaptive thresholding
3. Confidence estimation
4. Explainability

Research basis: Multi-metric fusion from SEED and Dual-GCN
"""

from typing import Dict, Tuple, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EnsembleClassifier:
    """
    Ensemble classifier for semantic clone detection
    
    Combines multiple metrics intelligently:
    - Weights metrics by importance
    - Adapts threshold based on consistency
    - Provides confidence scores
    - Generates explanations
    """
    
    def __init__(
        self,
        base_threshold: float = 0.65,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize ensemble classifier
        
        Args:
            base_threshold: Base detection threshold
            weights: Custom metric weights (optional)
        """
        self.base_threshold = base_threshold
        
        # Default weights (optimized for Type-4)
        self.weights = weights or {
            'ast_similarity': 0.15,           # Syntactic structure
            'control_flow_similarity': 0.35,  # Control patterns (IMPORTANT)
            'data_flow_similarity': 0.30,     # Data dependencies (IMPORTANT)
            'api_similarity': 0.15,           # API usage
            'signature_similarity': 0.05      # High-level summary
        }
        
        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v/total for k, v in self.weights.items()}
    
    def classify(
        self,
        similarities: Dict[str, float],
        language: str = "python"
    ) -> Dict:
        """
        Classify code pair as clone or non-clone
        
        Args:
            similarities: Dictionary of similarity scores
            language: Programming language
            
        Returns:
            Dictionary with:
            - is_clone: bool
            - final_score: float (0.0 to 1.0)
            - confidence: float (0.0 to 1.0)
            - threshold: float (actual threshold used)
            - explanation: str
            - per_metric: Dict (individual scores)
        """
        # Compute weighted score
        final_score = self._weighted_average(similarities)
        
        # Compute confidence
        confidence = self._compute_confidence(similarities)
        
        # Adaptive threshold
        threshold = self._adaptive_threshold(
            final_score,
            confidence,
            language
        )
        
        # Make decision
        is_clone = final_score >= threshold
        
        # Determine clone type
        clone_type = self._determine_clone_type(final_score, is_clone)
        
        # Generate explanation
        explanation = self._generate_explanation(
            similarities,
            final_score,
            threshold,
            confidence,
            is_clone
        )
        
        return {
            'is_clone': is_clone,
            'clone_type': clone_type,
            'final_score': final_score,
            'confidence': confidence,
            'threshold': threshold,
            'per_metric': similarities,
            'explanation': explanation
        }
    
    def _weighted_average(self, similarities: Dict[str, float]) -> float:
        """Compute weighted average of similarities"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, weight in self.weights.items():
            if metric in similarities:
                weighted_sum += similarities[metric] * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _compute_confidence(self, similarities: Dict[str, float]) -> float:
        """
        Compute confidence based on metric consistency
        
        Low variance = high confidence (metrics agree)
        High variance = low confidence (metrics disagree)
        """
        # Get relevant metric values
        values = [
            similarities[k] for k in self.weights.keys()
            if k in similarities
        ]
        
        if not values:
            return 0.0
        
        # Compute variance
        mean = np.mean(values)
        variance = np.var(values)
        
        # Convert variance to confidence
        # Low variance (< 0.01) = high confidence (> 0.9)
        # High variance (> 0.1) = low confidence (< 0.5)
        confidence = 1.0 - min(1.0, variance * 5)
        
        return max(0.0, confidence)
    
    def _adaptive_threshold(
        self,
        final_score: float,
        confidence: float,
        language: str
    ) -> float:
        """
        Adapt threshold based on confidence and language
        
        Strategy:
        - Low confidence → raise threshold (be more conservative)
        - High confidence → use base threshold
        - Some languages need adjustment
        """
        threshold = self.base_threshold
        
        # Confidence adjustment
        if confidence < 0.5:
            # Low confidence: increase threshold by up to 0.10
            adjustment = 0.10 * (0.5 - confidence) * 2
            threshold += adjustment
        elif confidence > 0.8:
            # High confidence: slightly decrease threshold
            adjustment = 0.05 * (confidence - 0.8) * 5
            threshold -= adjustment
        
        # Language-specific adjustment
        language_adjustments = {
            'python': 0.0,
            'java': 0.0,
            'javascript': -0.05,  # More lenient (dynamic language)
            'c': 0.05,            # More strict (structured language)
            'cpp': 0.05,          # More strict
            'go': 0.0,
            'php': -0.05
        }
        
        lang_adj = language_adjustments.get(language.lower(), 0.0)
        threshold += lang_adj
        
        # Clamp to reasonable range
        threshold = max(0.50, min(0.85, threshold))
        
        return threshold
    
    def _determine_clone_type(
        self,
        final_score: float,
        is_clone: bool
    ) -> str:
        """
        Determine clone type based on similarity score
        
        Type-1: Identical (95%+)
        Type-2: Renamed (85-95%)
        Type-3: Modified (70-85%)
        Type-4: Semantic (55-70%)
        """
        if not is_clone:
            return "Not-Clone"
        
        if final_score >= 0.95:
            return "Type-1"
        elif final_score >= 0.85:
            return "Type-2"
        elif final_score >= 0.70:
            return "Type-3"
        else:
            return "Type-4"
    
    def _generate_explanation(
        self,
        similarities: Dict[str, float],
        final_score: float,
        threshold: float,
        confidence: float,
        is_clone: bool
    ) -> str:
        """Generate human-readable explanation"""
        
        lines = []
        
        # Overall decision
        decision = "CLONE DETECTED" if is_clone else "NOT A CLONE"
        lines.append(f"Decision: {decision}")
        lines.append(f"Final Score: {final_score:.2%} (threshold: {threshold:.2%})")
        lines.append(f"Confidence: {confidence:.2%}")
        lines.append("")
        
        # Per-metric breakdown
        lines.append("Metric Breakdown:")
        for metric, score in sorted(similarities.items(), key=lambda x: x[1], reverse=True):
            weight = self.weights.get(metric, 0.0)
            contribution = score * weight
            
            # Visual indicator
            bar_length = int(score * 20)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            
            lines.append(
                f"  {metric:25s}: {score:.2%} {bar} "
                f"(weight: {weight:.0%}, contribution: {contribution:.2%})"
            )
        
        lines.append("")
        
        # Analysis
        lines.append("Analysis:")
        
        # Identify strengths
        strong_metrics = [m for m, s in similarities.items() if s >= 0.75]
        if strong_metrics:
            lines.append(f"  Strong similarities: {', '.join(strong_metrics)}")
        
        # Identify weaknesses
        weak_metrics = [m for m, s in similarities.items() if s < 0.50]
        if weak_metrics:
            lines.append(f"  Weak similarities: {', '.join(weak_metrics)}")
        
        # Confidence explanation
        if confidence < 0.5:
            lines.append(
                "  ⚠ Low confidence: Metrics show inconsistent results. "
                "Manual review recommended."
            )
        elif confidence > 0.8:
            lines.append(
                "  ✓ High confidence: Metrics are consistent and reliable."
            )
        
        return "\n".join(lines)
    
    def set_weights(self, weights: Dict[str, float]):
        """Update metric weights"""
        total = sum(weights.values())
        self.weights = {k: v/total for k, v in weights.items()}
    
    def set_threshold(self, threshold: float):
        """Update base threshold"""
        self.base_threshold = max(0.0, min(1.0, threshold))


def get_ensemble_classifier(
    base_threshold: float = 0.65,
    weights: Optional[Dict[str, float]] = None
) -> EnsembleClassifier:
    """
    Get EnsembleClassifier instance
    
    Args:
        base_threshold: Base detection threshold
        weights: Custom metric weights
        
    Returns:
        EnsembleClassifier instance
    """
    return EnsembleClassifier(base_threshold, weights)