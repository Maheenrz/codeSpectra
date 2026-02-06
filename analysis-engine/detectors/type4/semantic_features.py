# analysis-engine/detectors/type4/semantic_features.py

"""
Semantic Feature Extraction for Type-4 Clone Detection

Extracts high-level semantic features from PDG that capture:
1. Control flow patterns (how the code flows)
2. Data flow patterns (how data moves)
3. API/Call patterns (what functions are called)
4. Structural patterns (shape of the code)
5. Behavioral patterns (overall behavior signature)

These features are LANGUAGE-AGNOSTIC - they capture WHAT the code does,
not HOW it's written syntactically.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple
from collections import Counter
import numpy as np

from .pdg_builder import SimplifiedPDG, PDGNode


# =============================================================================
# SEMANTIC FEATURES DATA STRUCTURE
# =============================================================================

@dataclass
class SemanticFeatures:
    """
    Semantic features extracted from a code unit.
    
    These features capture the BEHAVIOR of code, not its syntax.
    Two codes with similar features likely do similar things.
    """
    
    # === Control Flow Features ===
    loop_count: int = 0                     # How many loops?
    condition_count: int = 0                # How many if/switch?
    max_nesting_depth: int = 0              # How deep is nesting?
    has_recursion: bool = False             # Does function call itself?
    control_signature: str = ""             # Pattern like "LLCR"
    
    # === Data Flow Features ===
    variable_count: int = 0                 # How many unique variables?
    data_dependencies: int = 0              # How many data flow edges?
    def_use_ratio: float = 0.0              # Ratio of definitions to uses
    
    # === API/Call Features ===
    call_count: int = 0                     # Total function calls
    unique_calls: int = 0                   # Unique functions called
    call_sequence: List[str] = field(default_factory=list)  # Order of calls
    
    # === Structural Features ===
    node_count: int = 0                     # Total PDG nodes
    edge_count: int = 0                     # Total PDG edges  
    return_count: int = 0                   # How many return statements?
    
    # === Behavioral Hash (using buckets) ===
    iteration_bucket: str = ""              # LOOP, REC, or DIRECT
    complexity_bucket: str = ""             # SIMPLE, MODERATE, COMPLEX, VERY_COMPLEX
    nesting_bucket: str = ""                # FLAT, NESTED, DEEP
    data_bucket: str = ""                   # FEW_VARS, MOD_VARS, MANY_VARS
    call_bucket: str = ""                   # NO_CALLS, FEW_CALLS, MANY_CALLS
    return_bucket: str = ""                 # SINGLE_RET, MULTI_RET, MANY_RET
    
    # Combined behavioral hash
    behavioral_hash: str = ""


# =============================================================================
# SEMANTIC FEATURE EXTRACTOR
# =============================================================================

class SemanticFeatureExtractor:
    """
    Extracts semantic features from a PDG.
    
    The extractor:
    1. Reads the PDG structure
    2. Extracts numeric features in 5 categories
    3. Creates behavioral buckets for hash comparison
    4. Combines into a behavioral hash
    """
    
    def __init__(self):
        pass
    
    def extract(self, pdg: SimplifiedPDG) -> SemanticFeatures:
        """
        Extract all semantic features from a PDG.
        
        Args:
            pdg: The SimplifiedPDG to extract features from
            
        Returns:
            SemanticFeatures object with all extracted features
        """
        
        # === Control Flow Features ===
        loop_count = pdg.loop_count
        condition_count = pdg.condition_count
        max_nesting = pdg.max_nesting_depth
        has_recursion = pdg.recursion_detected
        control_signature = pdg.control_flow_signature
        
        # === Data Flow Features ===
        variable_count = pdg.total_variables
        data_dependencies = pdg.total_data_dependencies
        
        # Calculate def/use ratio
        total_defs = sum(len(n.variables_defined) for n in pdg.nodes)
        total_uses = sum(len(n.variables_used) for n in pdg.nodes)
        def_use_ratio = total_defs / max(total_uses, 1)
        
        # === API/Call Features ===
        all_calls = []
        for node in pdg.nodes:
            all_calls.extend(node.function_calls)
        
        call_count = len(all_calls)
        unique_calls = len(set(all_calls))
        call_sequence = all_calls[:20]  # Keep first 20 calls
        
        # === Structural Features ===
        node_count = len(pdg.nodes)
        edge_count = len(pdg.edges)
        return_count = pdg.return_count
        
        # === Behavioral Buckets ===
        iteration_bucket = self._get_iteration_bucket(loop_count, has_recursion)
        complexity_bucket = self._get_complexity_bucket(loop_count, condition_count)
        nesting_bucket = self._get_nesting_bucket(max_nesting)
        data_bucket = self._get_data_bucket(variable_count)
        call_bucket = self._get_call_bucket(unique_calls)
        return_bucket = self._get_return_bucket(return_count)
        
        # === Behavioral Hash ===
        behavioral_hash = (
            f"{iteration_bucket}|{complexity_bucket}|{nesting_bucket}|"
            f"{data_bucket}|{call_bucket}|{return_bucket}"
        )
        
        return SemanticFeatures(
            # Control flow
            loop_count=loop_count,
            condition_count=condition_count,
            max_nesting_depth=max_nesting,
            has_recursion=has_recursion,
            control_signature=control_signature,
            
            # Data flow
            variable_count=variable_count,
            data_dependencies=data_dependencies,
            def_use_ratio=round(def_use_ratio, 2),
            
            # Calls
            call_count=call_count,
            unique_calls=unique_calls,
            call_sequence=call_sequence,
            
            # Structure
            node_count=node_count,
            edge_count=edge_count,
            return_count=return_count,
            
            # Buckets
            iteration_bucket=iteration_bucket,
            complexity_bucket=complexity_bucket,
            nesting_bucket=nesting_bucket,
            data_bucket=data_bucket,
            call_bucket=call_bucket,
            return_bucket=return_bucket,
            behavioral_hash=behavioral_hash,
        )
    
    # =========================================================================
    # BEHAVIORAL BUCKET METHODS
    # =========================================================================
    
    def _get_iteration_bucket(self, loop_count: int, has_recursion: bool) -> str:
        """
        Determine iteration pattern bucket.
        
        LOOP: Uses loops for iteration
        REC: Uses recursion
        DIRECT: Direct computation (no iteration)
        """
        if has_recursion:
            return "REC"
        elif loop_count > 0:
            return "LOOP"
        else:
            return "DIRECT"
    
    def _get_complexity_bucket(self, loop_count: int, condition_count: int) -> str:
        """
        Determine control flow complexity bucket.
        
        Based on total number of control structures.
        """
        total = loop_count + condition_count
        
        if total == 0:
            return "SIMPLE"
        elif total <= 2:
            return "MODERATE"
        elif total <= 5:
            return "COMPLEX"
        else:
            return "VERY_COMPLEX"
    
    def _get_nesting_bucket(self, max_nesting: int) -> str:
        """
        Determine nesting depth bucket.
        """
        if max_nesting <= 1:
            return "FLAT"
        elif max_nesting <= 3:
            return "NESTED"
        else:
            return "DEEP"
    
    def _get_data_bucket(self, variable_count: int) -> str:
        """
        Determine data complexity bucket.
        """
        if variable_count <= 3:
            return "FEW_VARS"
        elif variable_count <= 7:
            return "MOD_VARS"
        else:
            return "MANY_VARS"
    
    def _get_call_bucket(self, unique_calls: int) -> str:
        """
        Determine function call pattern bucket.
        """
        if unique_calls == 0:
            return "NO_CALLS"
        elif unique_calls <= 2:
            return "FEW_CALLS"
        else:
            return "MANY_CALLS"
    
    def _get_return_bucket(self, return_count: int) -> str:
        """
        Determine return pattern bucket.
        """
        if return_count <= 1:
            return "SINGLE_RET"
        elif return_count <= 3:
            return "MULTI_RET"
        else:
            return "MANY_RET"
    
    # =========================================================================
    # PAIR COMPARISON METHODS
    # =========================================================================
    
    def compute_pair_features(
        self,
        feat_a: SemanticFeatures,
        feat_b: SemanticFeatures
    ) -> Dict[str, float]:
        """
        Compute similarity features between two semantic feature sets.
        
        Returns a dictionary of similarity scores (0.0 to 1.0) for each feature.
        """
        
        # === Control Flow Similarities ===
        loop_sim = self._compute_count_similarity(
            feat_a.loop_count, feat_b.loop_count
        )
        condition_sim = self._compute_count_similarity(
            feat_a.condition_count, feat_b.condition_count
        )
        nesting_sim = self._compute_count_similarity(
            feat_a.max_nesting_depth, feat_b.max_nesting_depth
        )
        recursion_match = 1.0 if feat_a.has_recursion == feat_b.has_recursion else 0.0
        control_sig_sim = self._compute_signature_similarity(
            feat_a.control_signature, feat_b.control_signature
        )
        
        # === Data Flow Similarities ===
        variable_sim = self._compute_count_similarity(
            feat_a.variable_count, feat_b.variable_count
        )
        dependency_sim = self._compute_count_similarity(
            feat_a.data_dependencies, feat_b.data_dependencies
        )
        def_use_sim = 1.0 - abs(feat_a.def_use_ratio - feat_b.def_use_ratio) / max(
            feat_a.def_use_ratio + feat_b.def_use_ratio, 0.01
        )
        def_use_sim = max(0.0, min(1.0, def_use_sim))
        
        # === Call Pattern Similarities ===
        call_count_sim = self._compute_count_similarity(
            feat_a.call_count, feat_b.call_count
        )
        unique_call_sim = self._compute_count_similarity(
            feat_a.unique_calls, feat_b.unique_calls
        )
        call_overlap_sim = self._compute_call_overlap(
            feat_a.call_sequence, feat_b.call_sequence
        )
        
        # === Structural Similarities ===
        node_sim = self._compute_count_similarity(
            feat_a.node_count, feat_b.node_count
        )
        edge_sim = self._compute_count_similarity(
            feat_a.edge_count, feat_b.edge_count
        )
        return_sim = 1.0 if feat_a.return_count == feat_b.return_count else (
            0.5 if abs(feat_a.return_count - feat_b.return_count) <= 1 else 0.0
        )
        
        # === Behavioral Hash Similarity ===
        behavioral_sim = self._compute_behavioral_hash_similarity(
            feat_a.behavioral_hash, feat_b.behavioral_hash
        )
        
        # === Bucket Matches ===
        iteration_match = 1.0 if feat_a.iteration_bucket == feat_b.iteration_bucket else 0.0
        complexity_match = 1.0 if feat_a.complexity_bucket == feat_b.complexity_bucket else 0.5
        nesting_match = 1.0 if feat_a.nesting_bucket == feat_b.nesting_bucket else 0.5
        data_match = 1.0 if feat_a.data_bucket == feat_b.data_bucket else 0.5
        call_match = 1.0 if feat_a.call_bucket == feat_b.call_bucket else 0.5
        return_match = 1.0 if feat_a.return_bucket == feat_b.return_bucket else 0.5
        
        return {
            # Control flow
            'loop_similarity': round(loop_sim, 4),
            'condition_similarity': round(condition_sim, 4),
            'nesting_similarity': round(nesting_sim, 4),
            'recursion_match': recursion_match,
            'control_signature_similarity': round(control_sig_sim, 4),
            
            # Data flow
            'variable_similarity': round(variable_sim, 4),
            'dependency_similarity': round(dependency_sim, 4),
            'def_use_similarity': round(def_use_sim, 4),
            
            # Calls
            'call_count_similarity': round(call_count_sim, 4),
            'unique_call_similarity': round(unique_call_sim, 4),
            'call_overlap_similarity': round(call_overlap_sim, 4),
            
            # Structure
            'node_similarity': round(node_sim, 4),
            'edge_similarity': round(edge_sim, 4),
            'return_similarity': return_sim,
            
            # Behavioral
            'behavioral_hash_similarity': round(behavioral_sim, 4),
            'iteration_bucket_match': iteration_match,
            'complexity_bucket_match': complexity_match,
            'nesting_bucket_match': nesting_match,
            'data_bucket_match': data_match,
            'call_bucket_match': call_match,
            'return_bucket_match': return_match,
        }
    
    def _compute_count_similarity(self, count_a: int, count_b: int) -> float:
        """
        Compute similarity between two counts.
        
        Uses formula: 1 - |a - b| / max(a + b, 1)
        Returns 1.0 when equal, decreases as difference increases.
        """
        if count_a == count_b:
            return 1.0
        
        total = count_a + count_b
        if total == 0:
            return 1.0
        
        diff = abs(count_a - count_b)
        return 1.0 - (diff / total)
    
    def _compute_signature_similarity(self, sig_a: str, sig_b: str) -> float:
        """
        Compute similarity between control flow signatures.
        
        Uses character frequency overlap (Jaccard-like).
        """
        if not sig_a and not sig_b:
            return 1.0
        if not sig_a or not sig_b:
            return 0.0
        
        counter_a = Counter(sig_a)
        counter_b = Counter(sig_b)
        
        # Intersection and union of character counts
        common = sum((counter_a & counter_b).values())
        total = sum((counter_a | counter_b).values())
        
        return common / total if total > 0 else 0.0
    
    def _compute_call_overlap(self, calls_a: List[str], calls_b: List[str]) -> float:
        """
        Compute overlap between function call sequences.
        """
        if not calls_a and not calls_b:
            return 1.0
        if not calls_a or not calls_b:
            return 0.0
        
        set_a = set(calls_a)
        set_b = set(calls_b)
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _compute_behavioral_hash_similarity(self, hash_a: str, hash_b: str) -> float:
        """
        Compute similarity between behavioral hashes.
        
        Hashes are in format: "BUCKET1|BUCKET2|BUCKET3|..."
        Compares bucket by bucket and returns fraction of matches.
        """
        if not hash_a or not hash_b:
            return 0.0
        
        parts_a = hash_a.split('|')
        parts_b = hash_b.split('|')
        
        if len(parts_a) != len(parts_b):
            return 0.0
        
        matches = sum(1 for a, b in zip(parts_a, parts_b) if a == b)
        return matches / len(parts_a)
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def to_vector(self, features: SemanticFeatures) -> np.ndarray:
        """
        Convert semantic features to a numeric vector for ML.
        
        Returns a numpy array of numeric feature values.
        """
        return np.array([
            features.loop_count,
            features.condition_count,
            features.max_nesting_depth,
            int(features.has_recursion),
            features.variable_count,
            features.data_dependencies,
            features.def_use_ratio,
            features.call_count,
            features.unique_calls,
            features.node_count,
            features.edge_count,
            features.return_count,
            len(features.control_signature),
        ], dtype=np.float32)
    
    def to_dict(self, features: SemanticFeatures) -> Dict:
        """Convert SemanticFeatures to dictionary for JSON serialization."""
        return {
            'loop_count': features.loop_count,
            'condition_count': features.condition_count,
            'max_nesting_depth': features.max_nesting_depth,
            'has_recursion': features.has_recursion,
            'control_signature': features.control_signature,
            'variable_count': features.variable_count,
            'data_dependencies': features.data_dependencies,
            'def_use_ratio': features.def_use_ratio,
            'call_count': features.call_count,
            'unique_calls': features.unique_calls,
            'node_count': features.node_count,
            'edge_count': features.edge_count,
            'return_count': features.return_count,
            'behavioral_hash': features.behavioral_hash,
            'buckets': {
                'iteration': features.iteration_bucket,
                'complexity': features.complexity_bucket,
                'nesting': features.nesting_bucket,
                'data': features.data_bucket,
                'calls': features.call_bucket,
                'returns': features.return_bucket,
            }
        }