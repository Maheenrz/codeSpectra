# detectors/type4/joern/ml/codebert_integration.py

"""
CodeBERT Integration for Type-4 Clone Detection

CodeBERT: Microsoft's pre-trained BERT model for code
- Trained on 6 programming languages
- Understands code semantics
- Can generate embeddings for similarity comparison

FREE to use: Run locally via HuggingFace Transformers
NO API KEY needed: Just download model once

When to use CodeBERT:
- When Joern metrics are inconclusive (confidence < 0.5)
- When final score is near threshold (±0.10)
- As a tiebreaker between close scores
- For cross-language comparison (future feature)

Installation:
    pip install transformers torch
    
First run downloads model (~500MB) - subsequent runs use cached version
"""

import logging
from typing import Optional, Dict, Tuple
import numpy as np

logger = logging.getLogger(__name__)

# Optional import - won't crash if not installed
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    CODEBERT_AVAILABLE = True
except ImportError:
    CODEBERT_AVAILABLE = False
    logger.warning(
        "CodeBERT not available. Install with: pip install transformers torch"
    )


class CodeBERTIntegration:
    """
    CodeBERT-based semantic similarity computation
    
    Uses Microsoft's CodeBERT model to:
    1. Generate code embeddings
    2. Compute semantic similarity via cosine distance
    3. Provide additional confidence signal
    
    Example:
        codebert = CodeBERTIntegration()
        similarity = codebert.compute_similarity(code1, code2, "python")
        print(f"CodeBERT similarity: {similarity:.2%}")
    """
    
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        """
        Initialize CodeBERT
        
        Args:
            model_name: HuggingFace model identifier
                       Options:
                       - "microsoft/codebert-base" (recommended)
                       - "microsoft/graphcodebert-base" (advanced)
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = None
        
        if CODEBERT_AVAILABLE:
            self._initialize_model()
        else:
            logger.warning(
                "CodeBERT integration disabled. "
                "Install transformers and torch to enable."
            )
    
    def _initialize_model(self):
        """Load CodeBERT model and tokenizer"""
        try:
            logger.info(f"Loading CodeBERT model: {self.model_name}")
            logger.info("First run will download ~500MB model (one-time only)")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # Set device (GPU if available, else CPU)
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            logger.info(f"CodeBERT loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load CodeBERT: {e}")
            self.tokenizer = None
            self.model = None
    
    def is_available(self) -> bool:
        """Check if CodeBERT is available"""
        return self.tokenizer is not None and self.model is not None
    
    def get_embedding(
        self,
        code: str,
        language: str = "python"
    ) -> Optional[np.ndarray]:
        """
        Generate code embedding
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Embedding vector (768-dimensional) or None if error
        """
        if not self.is_available():
            return None
        
        try:
            # Prepare input
            # CodeBERT format: <language> code </language>
            formatted_code = f"<{language}> {code} </{language}>"
            
            # Tokenize (max length 512 tokens)
            tokens = self.tokenizer(
                formatted_code,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # Move to device
            tokens = {k: v.to(self.device) for k, v in tokens.items()}
            
            # Get embeddings (no gradient computation)
            with torch.no_grad():
                outputs = self.model(**tokens)
            
            # Get [CLS] token embedding (sentence-level)
            # Alternative: mean pool all tokens
            embedding = outputs.last_hidden_state[:, 0, :].squeeze()
            
            # Convert to numpy
            embedding = embedding.cpu().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def compute_similarity(
        self,
        code1: str,
        code2: str,
        language: str = "python"
    ) -> float:
        """
        Compute semantic similarity using CodeBERT
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            language: Programming language
            
        Returns:
            Similarity score (0.0 to 1.0), or 0.0 if error
        """
        if not self.is_available():
            logger.warning("CodeBERT not available, returning 0.0")
            return 0.0
        
        # Get embeddings
        emb1 = self.get_embedding(code1, language)
        emb2 = self.get_embedding(code2, language)
        
        if emb1 is None or emb2 is None:
            logger.error("Failed to generate embeddings")
            return 0.0
        
        # Compute cosine similarity
        similarity = self._cosine_similarity(emb1, emb2)
        
        return similarity
    
    def should_use_codebert(
        self,
        joern_result: Dict,
        threshold_margin: float = 0.10
    ) -> bool:
        """
        Determine if CodeBERT should be used as tiebreaker
        
        Use CodeBERT when:
        1. Confidence is low (< 0.5)
        2. Score is near threshold (±0.10)
        3. Joern metrics are inconclusive
        
        Args:
            joern_result: Result from Joern detector
            threshold_margin: Margin around threshold
            
        Returns:
            True if CodeBERT should be used
        """
        if not self.is_available():
            return False
        
        confidence = joern_result.get('confidence', 1.0)
        final_score = joern_result.get('final_score', 0.0)
        threshold = joern_result.get('threshold', 0.65)
        
        # Use CodeBERT if:
        # 1. Low confidence
        if confidence < 0.5:
            return True
        
        # 2. Score near threshold
        if abs(final_score - threshold) < threshold_margin:
            return True
        
        # 3. Metrics highly inconsistent
        per_metric = joern_result.get('per_metric', {})
        if per_metric:
            values = list(per_metric.values())
            variance = np.var(values)
            if variance > 0.15:  # High variance
                return True
        
        return False
    
    def enhance_result(
        self,
        code1: str,
        code2: str,
        joern_result: Dict,
        language: str = "python",
        codebert_weight: float = 0.30
    ) -> Dict:
        """
        Enhance Joern result with CodeBERT
        
        Combines Joern and CodeBERT scores:
        final_score = (1 - w) * joern_score + w * codebert_score
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            joern_result: Result from Joern detector
            language: Programming language
            codebert_weight: Weight for CodeBERT score (0.0 to 1.0)
            
        Returns:
            Enhanced result dictionary
        """
        if not self.is_available():
            logger.warning("CodeBERT not available, returning original result")
            return joern_result
        
        # Compute CodeBERT similarity
        codebert_sim = self.compute_similarity(code1, code2, language)
        
        # Get original Joern score
        joern_score = joern_result.get('final_score', 0.0)
        
        # Combine scores
        combined_score = (
            (1 - codebert_weight) * joern_score +
            codebert_weight * codebert_sim
        )
        
        # Update result
        enhanced_result = joern_result.copy()
        enhanced_result['final_score'] = combined_score
        enhanced_result['codebert_similarity'] = codebert_sim
        enhanced_result['joern_similarity'] = joern_score
        enhanced_result['codebert_weight'] = codebert_weight
        enhanced_result['enhanced_by_codebert'] = True
        
        # Re-evaluate is_clone with combined score
        threshold = joern_result.get('threshold', 0.65)
        enhanced_result['is_clone'] = combined_score >= threshold
        
        # Update explanation
        original_exp = joern_result.get('explanation', '')
        enhanced_exp = (
            f"{original_exp}\n\n"
            f"Enhanced with CodeBERT:\n"
            f"  Joern Score: {joern_score:.2%}\n"
            f"  CodeBERT Score: {codebert_sim:.2%}\n"
            f"  Combined Score: {combined_score:.2%} "
            f"(Joern: {1-codebert_weight:.0%}, CodeBERT: {codebert_weight:.0%})"
        )
        enhanced_result['explanation'] = enhanced_exp
        
        return enhanced_result
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to [0, 1] (cosine is in [-1, 1])
        similarity = (similarity + 1) / 2
        
        return float(similarity)
    
    def clear_cache(self):
        """Clear model from memory"""
        if self.model is not None:
            del self.model
            self.model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Singleton instance
_codebert_instance: Optional[CodeBERTIntegration] = None


def get_codebert_integration() -> CodeBERTIntegration:
    """
    Get CodeBERT integration instance (singleton)
    
    Returns:
        CodeBERTIntegration instance
    """
    global _codebert_instance
    
    if _codebert_instance is None:
        _codebert_instance = CodeBERTIntegration()
    
    return _codebert_instance


def is_codebert_available() -> bool:
    """Check if CodeBERT is available"""
    return CODEBERT_AVAILABLE