# detectors/type4/joern/models/semantic_result.py

"""
Semantic Clone Detection Result Models

Focused purely on Type-4 semantic clone detection.
Simple, clear output: Is it a semantic clone? How similar?
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime


class ConfidenceLevel(Enum):
    """Confidence in the semantic clone detection"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SemanticScores:
    """
    Detailed similarity scores for semantic comparison
    """
    # Overall semantic similarity (0.0 to 1.0)
    overall: float = 0.0
    
    # Component scores
    node_type_similarity: float = 0.0      # Similar operations?
    control_flow_similarity: float = 0.0   # Similar control structure?
    data_flow_similarity: float = 0.0      # Similar data dependencies?
    structural_similarity: float = 0.0     # Similar graph shape?
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "overall": round(self.overall, 4),
            "node_type_similarity": round(self.node_type_similarity, 4),
            "control_flow_similarity": round(self.control_flow_similarity, 4),
            "data_flow_similarity": round(self.data_flow_similarity, 4),
            "structural_similarity": round(self.structural_similarity, 4)
        }
    
    def to_percentages(self) -> Dict[str, str]:
        return {
            "overall": f"{self.overall * 100:.1f}%",
            "node_type_similarity": f"{self.node_type_similarity * 100:.1f}%",
            "control_flow_similarity": f"{self.control_flow_similarity * 100:.1f}%",
            "data_flow_similarity": f"{self.data_flow_similarity * 100:.1f}%",
            "structural_similarity": f"{self.structural_similarity * 100:.1f}%"
        }


@dataclass
class PDGInfo:
    """Information about extracted PDG"""
    num_methods: int = 0
    num_nodes: int = 0
    num_edges: int = 0
    num_control_edges: int = 0
    num_data_edges: int = 0
    method_names: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_methods": self.num_methods,
            "num_nodes": self.num_nodes,
            "num_edges": self.num_edges,
            "num_control_edges": self.num_control_edges,
            "num_data_edges": self.num_data_edges,
            "method_names": self.method_names
        }


@dataclass
class SemanticCloneResult:
    """
    Result of Type-4 Semantic Clone Detection
    
    Simple, focused output:
    - is_semantic_clone: True/False
    - similarity: 0.0 to 1.0
    - confidence: high/medium/low
    """
    
    # Core result
    is_semantic_clone: bool = False
    similarity: float = 0.0
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    
    # Status
    status: str = "pending"  # "success", "error", "pending"
    error_message: Optional[str] = None
    
    # Language
    language: str = "unknown"
    
    # Detailed scores
    scores: SemanticScores = field(default_factory=SemanticScores)
    
    # PDG information
    pdg1_info: PDGInfo = field(default_factory=PDGInfo)
    pdg2_info: PDGInfo = field(default_factory=PDGInfo)
    
    # File paths (if comparing files)
    code1_path: Optional[str] = None
    code2_path: Optional[str] = None
    
    # Threshold used
    threshold_used: float = 0.55
    
    # Timing
    analysis_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_semantic_clone": self.is_semantic_clone,
            "similarity": round(self.similarity, 4),
            "similarity_percent": f"{self.similarity * 100:.1f}%",
            "confidence": self.confidence.value,
            "status": self.status,
            "error_message": self.error_message,
            "language": self.language,
            "scores": self.scores.to_dict(),
            "pdg1_info": self.pdg1_info.to_dict(),
            "pdg2_info": self.pdg2_info.to_dict(),
            "code1_path": self.code1_path,
            "code2_path": self.code2_path,
            "threshold_used": self.threshold_used,
            "analysis_time_ms": round(self.analysis_time_ms, 2),
            "timestamp": self.timestamp
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        if self.status == "error":
            return f"Error: {self.error_message}"
        
        clone_status = "YES" if self.is_semantic_clone else "NO"
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║            TYPE-4 SEMANTIC CLONE DETECTION RESULT            ║
╠══════════════════════════════════════════════════════════════╣
║  Is Semantic Clone:  {clone_status:<39} ║
║  Similarity:         {self.similarity * 100:>6.1f}%{' ' * 32}║
║  Confidence:         {self.confidence.value:<39} ║
║  Language:           {self.language:<39} ║
╠══════════════════════════════════════════════════════════════╣
║  DETAILED SCORES:                                            ║
║    Node Types:       {self.scores.node_type_similarity * 100:>6.1f}%{' ' * 32}║
║    Control Flow:     {self.scores.control_flow_similarity * 100:>6.1f}%{' ' * 32}║
║    Data Flow:        {self.scores.data_flow_similarity * 100:>6.1f}%{' ' * 32}║
║    Structure:        {self.scores.structural_similarity * 100:>6.1f}%{' ' * 32}║
╠══════════════════════════════════════════════════════════════╣
║  Threshold Used:     {self.threshold_used * 100:>6.1f}%{' ' * 32}║
║  Analysis Time:      {self.analysis_time_ms:>6.1f} ms{' ' * 30}║
╚══════════════════════════════════════════════════════════════╝
"""


@dataclass
class BatchSemanticResult:
    """Results for batch semantic clone detection"""
    
    results: List[SemanticCloneResult] = field(default_factory=list)
    total_comparisons: int = 0
    semantic_clones_found: int = 0
    total_time_ms: float = 0.0
    
    def add_result(self, result: SemanticCloneResult):
        self.results.append(result)
        self.total_comparisons += 1
        if result.is_semantic_clone:
            self.semantic_clones_found += 1
    
    def get_summary(self) -> str:
        rate = (self.semantic_clones_found / self.total_comparisons * 100) if self.total_comparisons > 0 else 0
        return f"""
Batch Semantic Clone Detection:
  Total Comparisons: {self.total_comparisons}
  Semantic Clones Found: {self.semantic_clones_found}
  Detection Rate: {rate:.1f}%
  Total Time: {self.total_time_ms:.2f} ms
"""