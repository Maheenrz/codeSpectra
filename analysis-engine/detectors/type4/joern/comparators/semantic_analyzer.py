# detectors/type4/joern/comparators/semantic_analyzer.py

"""
Semantic Analyzer for Type-4 Clone Detection

Focuses purely on BEHAVIORAL similarity:
- Do the codes perform similar operations?
- Do they have similar control flow patterns?
- Do they have similar data flow patterns?

Ignores:
- Variable names
- Function names
- Exact syntax
- Minor structural differences
"""

from typing import List, Tuple, Dict, Set
from collections import Counter

try:
    from ..models import (
        PDG, 
        MethodPDG, 
        PDGNode, 
        PDGEdge, 
        EdgeType,
        SemanticScores,
        ConfidenceLevel
    )
    from ..config import get_config, get_semantic_config
except ImportError:
    from models import (
        PDG, 
        MethodPDG, 
        PDGNode, 
        PDGEdge, 
        EdgeType,
        SemanticScores,
        ConfidenceLevel
    )
    from config import get_config, get_semantic_config


class SemanticAnalyzer:
    """
    Analyzes semantic similarity between two PDGs for Type-4 clone detection.
    
    Type-4 clones: Same functionality, different implementation.
    Examples:
    - Recursive vs Iterative
    - Array vs LinkedList
    - Different algorithms for same result
    """
    
    def __init__(self):
        self.config = get_config()
        self.semantic_config = get_semantic_config()
        
        # Semantic node categories - language agnostic
        self.node_categories = {
            'CONTROL': {
                'CONTROL_STRUCTURE', 'IF', 'ELSE', 'WHILE', 'FOR', 
                'SWITCH', 'CASE', 'DO', 'FOREACH', 'TRY', 'CATCH'
            },
            'LOOP': {
                'WHILE', 'FOR', 'DO', 'FOREACH', 'FOR_EACH'
            },
            'BRANCH': {
                'IF', 'ELSE', 'SWITCH', 'CASE', 'TERNARY', 'CONDITIONAL'
            },
            'CALL': {
                'CALL', 'METHOD_CALL', 'FUNCTION_CALL', 'INVOKE'
            },
            'RETURN': {
                'RETURN', 'RETURN_VALUE', 'YIELD'
            },
            'ASSIGNMENT': {
                'ASSIGNMENT', 'ASSIGN', 'STORE', 'LOCAL', 'FIELD_ACCESS'
            },
            'ARITHMETIC': {
                'ADDITION', 'SUBTRACTION', 'MULTIPLICATION', 'DIVISION',
                'MODULO', 'INCREMENT', 'DECREMENT'
            },
            'COMPARISON': {
                'EQUALS', 'NOT_EQUALS', 'LESS_THAN', 'GREATER_THAN',
                'LESS_EQUALS', 'GREATER_EQUALS', 'COMPARE'
            },
            'LOGICAL': {
                'AND', 'OR', 'NOT', 'XOR', 'LOGICAL'
            },
            'VALUE': {
                'LITERAL', 'IDENTIFIER', 'PARAM', 'PARAMETER', 
                'CONSTANT', 'FIELD'
            }
        }
    
    def analyze(
        self, 
        pdg1: PDG, 
        pdg2: PDG,
        language: str = "python"
    ) -> Tuple[SemanticScores, ConfidenceLevel]:
        """
        Analyze semantic similarity between two PDGs.
        
        Returns:
            Tuple of (SemanticScores, ConfidenceLevel)
        """
        # Get all nodes and edges
        nodes1 = pdg1.get_all_nodes()
        nodes2 = pdg2.get_all_nodes()
        edges1 = pdg1.get_all_edges()
        edges2 = pdg2.get_all_edges()
        
        # Separate edge types
        control_edges1 = [e for e in edges1 if e.edge_type == EdgeType.CONTROL]
        control_edges2 = [e for e in edges2 if e.edge_type == EdgeType.CONTROL]
        data_edges1 = [e for e in edges1 if e.edge_type == EdgeType.DATA]
        data_edges2 = [e for e in edges2 if e.edge_type == EdgeType.DATA]
        
        # Calculate component similarities
        node_sim = self._calculate_node_type_similarity(nodes1, nodes2)
        control_sim = self._calculate_flow_similarity(
            control_edges1, control_edges2, nodes1, nodes2
        )
        data_sim = self._calculate_flow_similarity(
            data_edges1, data_edges2, nodes1, nodes2
        )
        struct_sim = self._calculate_structural_similarity(pdg1, pdg2)
        
        # Calculate weighted overall similarity
        weights = self.semantic_config.weights
        overall = (
            node_sim * weights["node_type_similarity"] +
            control_sim * weights["control_flow_similarity"] +
            data_sim * weights["data_flow_similarity"] +
            struct_sim * weights["structural_similarity"]
        )
        
        # Create scores
        scores = SemanticScores(
            overall=min(overall, 1.0),
            node_type_similarity=node_sim,
            control_flow_similarity=control_sim,
            data_flow_similarity=data_sim,
            structural_similarity=struct_sim
        )
        
        # Determine confidence
        confidence = self._determine_confidence(scores, language)
        
        return scores, confidence
    
    def _get_semantic_category(self, node: PDGNode) -> str:
        """Map node to semantic category"""
        label = node.label.upper()
        code = (node.code or "").upper()
        
        # Check against categories
        for category, keywords in self.node_categories.items():
            if label in keywords:
                return category
            # Also check code content for operators
            if category == 'ARITHMETIC' and any(op in code for op in ['+', '-', '*', '/', '%']):
                return category
            if category == 'COMPARISON' and any(op in code for op in ['==', '!=', '<', '>', '<=', '>=']):
                return category
        
        # Check for control structures in code
        code_lower = (node.code or "").lower()
        if any(kw in code_lower for kw in ['if', 'else', 'elif']):
            return 'BRANCH'
        if any(kw in code_lower for kw in ['for', 'while', 'do']):
            return 'LOOP'
        if 'return' in code_lower:
            return 'RETURN'
        
        return 'OTHER'
    
    def _calculate_node_type_similarity(
        self, 
        nodes1: List[PDGNode], 
        nodes2: List[PDGNode]
    ) -> float:
        """
        Calculate similarity based on node type distribution.
        This measures: Do both codes have similar TYPES of operations?
        """
        if not nodes1 and not nodes2:
            return 1.0
        if not nodes1 or not nodes2:
            return 0.0
        
        # Get category distributions
        cats1 = Counter(self._get_semantic_category(n) for n in nodes1)
        cats2 = Counter(self._get_semantic_category(n) for n in nodes2)
        
        # Calculate distribution similarity
        return self._distribution_similarity(cats1, cats2)
    
    def _calculate_flow_similarity(
        self,
        edges1: List[PDGEdge],
        edges2: List[PDGEdge],
        nodes1: List[PDGNode],
        nodes2: List[PDGNode]
    ) -> float:
        """
        Calculate similarity of flow patterns (control or data).
        This measures: Do both codes have similar FLOW patterns?
        """
        if not edges1 and not edges2:
            return 1.0
        if not edges1 or not edges2:
            return 0.0
        
        # Map node IDs to categories
        id_to_cat1 = {n.id: self._get_semantic_category(n) for n in nodes1}
        id_to_cat2 = {n.id: self._get_semantic_category(n) for n in nodes2}
        
        # Get edge patterns (category → category)
        patterns1 = Counter()
        for e in edges1:
            src = id_to_cat1.get(e.source_id, 'OTHER')
            tgt = id_to_cat1.get(e.target_id, 'OTHER')
            patterns1[(src, tgt)] += 1
        
        patterns2 = Counter()
        for e in edges2:
            src = id_to_cat2.get(e.source_id, 'OTHER')
            tgt = id_to_cat2.get(e.target_id, 'OTHER')
            patterns2[(src, tgt)] += 1
        
        # Calculate pattern distribution similarity
        dist_sim = self._distribution_similarity(patterns1, patterns2)
        
        # Calculate pattern set similarity (Jaccard)
        set1 = set(patterns1.keys())
        set2 = set(patterns2.keys())
        jaccard = len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 1.0
        
        # Combine: 60% distribution + 40% Jaccard
        return (dist_sim * 0.6) + (jaccard * 0.4)
    
    def _calculate_structural_similarity(self, pdg1: PDG, pdg2: PDG) -> float:
        """
        Calculate overall structural similarity.
        This measures: Do both codes have similar SHAPE?
        """
        n1, n2 = pdg1.total_nodes, pdg2.total_nodes
        e1, e2 = pdg1.total_edges, pdg2.total_edges
        c1, c2 = pdg1.total_control_edges, pdg2.total_control_edges
        d1, d2 = pdg1.total_data_edges, pdg2.total_data_edges
        
        # Node count similarity
        node_sim = min(n1, n2) / max(n1, n2) if max(n1, n2) > 0 else 1.0
        
        # Edge count similarity
        edge_sim = min(e1, e2) / max(e1, e2) if max(e1, e2) > 0 else 1.0
        
        # Control/Data ratio similarity
        ratio1 = c1 / (c1 + d1) if (c1 + d1) > 0 else 0.5
        ratio2 = c2 / (c2 + d2) if (c2 + d2) > 0 else 0.5
        ratio_sim = 1.0 - abs(ratio1 - ratio2)
        
        # Method count similarity
        m1, m2 = len(pdg1.methods), len(pdg2.methods)
        method_sim = min(m1, m2) / max(m1, m2) if max(m1, m2) > 0 else 1.0
        
        # Combine
        return (node_sim * 0.3) + (edge_sim * 0.3) + (ratio_sim * 0.2) + (method_sim * 0.2)
    
    def _distribution_similarity(self, dist1: Counter, dist2: Counter) -> float:
        """Calculate similarity between two distributions"""
        all_keys = set(dist1.keys()) | set(dist2.keys())
        
        if not all_keys:
            return 1.0
        
        # Normalize to percentages
        total1 = sum(dist1.values()) or 1
        total2 = sum(dist2.values()) or 1
        
        norm1 = {k: dist1.get(k, 0) / total1 for k in all_keys}
        norm2 = {k: dist2.get(k, 0) / total2 for k in all_keys}
        
        # Calculate similarity (1 - normalized difference)
        diff = sum(abs(norm1[k] - norm2[k]) for k in all_keys)
        max_diff = 2.0  # Maximum possible difference
        
        return 1.0 - (diff / max_diff)
    
    def _determine_confidence(
        self, 
        scores: SemanticScores, 
        language: str
    ) -> ConfidenceLevel:
        """Determine confidence level based on scores"""
        threshold = self.config.get_threshold_for_language(language)
        
        # High confidence: Well above threshold with good component scores
        if (scores.overall >= threshold + 0.20 and
            scores.control_flow_similarity >= 0.5 and
            scores.data_flow_similarity >= 0.5):
            return ConfidenceLevel.HIGH
        
        # Medium confidence: Above threshold with decent scores
        if (scores.overall >= threshold + 0.10 and
            (scores.control_flow_similarity >= 0.3 or scores.data_flow_similarity >= 0.5)):
            return ConfidenceLevel.MEDIUM
        
        # Low confidence: Just above threshold or mixed signals
        return ConfidenceLevel.LOW
    
    def is_semantic_clone(
        self, 
        pdg1: PDG, 
        pdg2: PDG,
        language: str = "python"
    ) -> bool:
        """Quick check if two PDGs represent semantic clones"""
        scores, _ = self.analyze(pdg1, pdg2, language)
        threshold = self.config.get_threshold_for_language(language)
        return scores.overall >= threshold


def get_semantic_analyzer() -> SemanticAnalyzer:
    """Get a SemanticAnalyzer instance"""
    return SemanticAnalyzer()