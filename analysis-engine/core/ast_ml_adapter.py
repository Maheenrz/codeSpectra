# ast_ml_adapter.py
"""
ASTMLAdapter: Provides ML-ready feature extraction from AST representations.
This module integrates with ASTProcessor to extract numerical feature vectors
suitable for machine learning models.
"""

import numpy as np
import os
from collections import Counter
from typing import List, Dict, Tuple, Optional

# Try relative import first, fall back to absolute import
try:
    from .ast_processor import ASTProcessor
except ImportError:
    from ast_processor import ASTProcessor


class ASTMLAdapter:
    """
    Adapter class that transforms AST-based code analysis into ML-ready feature vectors.
    Integrates with ASTProcessor for parsing and provides normalized feature extraction.
    """
    
    def __init__(self):
        self.ast_processor = ASTProcessor()
        # Define the set of structural node types we care about
        self.node_types = [
            'function_definition', 'method_declaration',
            'for_statement', 'while_statement', 'do_statement',
            'if_statement', 'else_clause',
            'try_statement', 'catch_clause',
            'switch_statement', 'case_statement',
            'return_statement', 'class_definition'
        ]
    
    def normalize_code(self, file_path: str) -> str:
        """
        Normalize code by extracting its structural skeleton.
        This is useful for comparing code at a structural level.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Normalized structural representation as a string
        """
        return self.ast_processor.get_structure_sequence(file_path)
    
    def extract_feature_vector(self, file_path: str) -> np.ndarray:
        """
        Extract a numerical feature vector from a code file.
        The vector includes:
        - Node type counts (frequency of each AST node type)
        - Structural depth metrics
        - Control flow complexity indicators
        
        Args:
            file_path: Path to the code file
            
        Returns:
            NumPy array representing the feature vector
        """
        # Get the structural sequence
        structure_seq = self.normalize_code(file_path)
        
        if not structure_seq:
            # Return zero vector if parsing failed
            return np.zeros(len(self.node_types) + 3)
        
        # Parse the structure sequence
        nodes = structure_seq.split()
        
        # Count occurrences of each node type
        node_counts = Counter(nodes)
        
        # Create feature vector with node type frequencies
        features = []
        for node_type in self.node_types:
            features.append(node_counts.get(node_type, 0))
        
        # Add aggregate metrics
        total_nodes = len(nodes)
        unique_nodes = len(set(nodes))
        control_flow_nodes = sum([
            node_counts.get('for_statement', 0),
            node_counts.get('while_statement', 0),
            node_counts.get('if_statement', 0),
            node_counts.get('switch_statement', 0)
        ])
        
        features.extend([total_nodes, unique_nodes, control_flow_nodes])
        
        return np.array(features, dtype=np.float32)
    
    def extract_feature_vector_normalized(self, file_path: str) -> np.ndarray:
        """
        Extract a normalized feature vector (0-1 range) from a code file.
        This is useful for ML models that work better with normalized inputs.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Normalized NumPy array representing the feature vector
        """
        features = self.extract_feature_vector(file_path)
        
        # Avoid division by zero
        max_val = np.max(features)
        if max_val > 0:
            features = features / max_val
        
        return features
    
    def batch_extract_features(self, file_paths: List[str], 
                               normalize: bool = False) -> np.ndarray:
        """
        Extract feature vectors for multiple files.
        
        Args:
            file_paths: List of paths to code files
            normalize: Whether to normalize the feature vectors
            
        Returns:
            2D NumPy array where each row is a feature vector
        """
        features_list = []
        
        for file_path in file_paths:
            if normalize:
                features = self.extract_feature_vector_normalized(file_path)
            else:
                features = self.extract_feature_vector(file_path)
            features_list.append(features)
        
        return np.array(features_list)
    
    def get_feature_names(self) -> List[str]:
        """
        Get the names of features in the feature vector.
        Useful for understanding what each dimension represents.
        
        Returns:
            List of feature names
        """
        feature_names = self.node_types.copy()
        feature_names.extend(['total_nodes', 'unique_nodes', 'control_flow_nodes'])
        return feature_names
    
    def extract_features_with_metadata(self, file_path: str) -> Dict:
        """
        Extract features along with metadata about the file.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Dictionary containing features, metadata, and structural info
        """
        features = self.extract_feature_vector(file_path)
        structure_seq = self.normalize_code(file_path)
        
        return {
            'file_path': file_path,
            'features': features,
            'feature_names': self.get_feature_names(),
            'structure_sequence': structure_seq,
            'feature_dimension': len(features)
        }
