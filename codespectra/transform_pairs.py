#!/usr/bin/env python3
"""
transform_pairs.py

Automates the transformation of pairs.csv by replacing symbolic file IDs
with their corresponding feature vectors extracted using ASTMLAdapter and ASTProcessor.

This script:
1. Reads pairs.csv with (unitA_id, unitB_id, label) format
2. Processes each referenced .cpp file in the dsa_dataset directory
3. Extracts feature vectors using ASTMLAdapter
4. Creates pairs_transformed.csv with format: [unitA_features, unitB_features, label]
"""

import sys
import os
import csv
import numpy as np
from pathlib import Path

# Add analysis-engine/core to the path so we can import the modules
script_dir = Path(__file__).parent.absolute()
core_dir = script_dir.parent / "analysis-engine" / "core"
sys.path.insert(0, str(core_dir))

from ast_ml_adapter import ASTMLAdapter


class PairsTransformer:
    """
    Transforms pairs.csv by replacing file IDs with feature vectors.
    """
    
    def __init__(self, dataset_dir: str):
        """
        Initialize the transformer.
        
        Args:
            dataset_dir: Path to the dsa_dataset directory
        """
        self.dataset_dir = Path(dataset_dir)
        self.adapter = ASTMLAdapter()
        self.feature_cache = {}
        
    def get_features(self, file_id: str) -> np.ndarray:
        """
        Get feature vector for a file, using cache if available.
        
        Args:
            file_id: Filename (e.g., 'binary_search.cpp')
            
        Returns:
            Feature vector as numpy array
        """
        if file_id in self.feature_cache:
            return self.feature_cache[file_id]
        
        file_path = self.dataset_dir / file_id
        
        if not file_path.exists():
            print(f"Warning: File {file_id} does not exist in dataset directory {self.dataset_dir}. Using zero vector.")
            features = np.zeros(len(self.adapter.get_feature_names()))
        else:
            features = self.adapter.extract_feature_vector(str(file_path))
        
        self.feature_cache[file_id] = features
        return features
    
    def transform_pairs(self, input_csv: str, output_csv: str):
        """
        Transform pairs.csv to pairs_transformed.csv.
        
        Args:
            input_csv: Path to input pairs.csv
            output_csv: Path to output pairs_transformed.csv
        """
        print(f"Reading pairs from: {input_csv}")
        print(f"Dataset directory: {self.dataset_dir}")
        
        input_path = Path(input_csv)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file {input_csv} not found")
        
        # Read input CSV
        pairs = []
        with open(input_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pairs.append({
                    'unitA_id': row['unitA_id'],
                    'unitB_id': row['unitB_id'],
                    'label': int(row['label'])
                })
        
        print(f"Found {len(pairs)} pairs to transform")
        
        # Transform pairs
        transformed_rows = []
        for i, pair in enumerate(pairs):
            print(f"Processing pair {i+1}/{len(pairs)}: {pair['unitA_id']} vs {pair['unitB_id']}")
            
            # Extract features
            features_a = self.get_features(pair['unitA_id'])
            features_b = self.get_features(pair['unitB_id'])
            label = pair['label']
            
            # Combine into single row: [features_a, features_b, label]
            row = np.concatenate([features_a, features_b, [label]])
            transformed_rows.append(row)
        
        # Convert to numpy array
        transformed_data = np.array(transformed_rows)
        
        # Write output CSV
        print(f"Writing transformed data to: {output_csv}")
        
        # Create header
        feature_names = self.adapter.get_feature_names()
        header = []
        for name in feature_names:
            header.append(f"unitA_{name}")
        for name in feature_names:
            header.append(f"unitB_{name}")
        header.append("label")
        
        # Write to CSV
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(transformed_data)
        
        print(f"Successfully created {output_csv}")
        print(f"Output shape: {transformed_data.shape}")
        print(f"Features per unit: {len(feature_names)}")
        print(f"Total columns: {len(header)}")
        
        return transformed_data
    
    def print_statistics(self):
        """
        Print statistics about the cached features.
        """
        if not self.feature_cache:
            print("No features cached yet.")
            return
        
        print("\n=== Feature Statistics ===")
        print(f"Files processed: {len(self.feature_cache)}")
        
        for file_id, features in self.feature_cache.items():
            print(f"\n{file_id}:")
            print(f"  Feature vector length: {len(features)}")
            print(f"  Non-zero elements: {np.count_nonzero(features)}")
            print(f"  Sum: {np.sum(features):.2f}")
            print(f"  Max: {np.max(features):.2f}")


def main():
    """
    Main function to run the transformation.
    """
    # Determine paths
    script_dir = Path(__file__).parent.absolute()
    dataset_dir = script_dir / "dsa_dataset"
    input_csv = dataset_dir / "pairs.csv"
    output_csv = dataset_dir / "pairs_transformed.csv"
    
    print("=== DSA Dataset Pairs Transformation ===")
    print(f"Script directory: {script_dir}")
    print(f"Dataset directory: {dataset_dir}")
    
    # Check if dataset directory exists
    if not dataset_dir.exists():
        print(f"Error: Dataset directory {dataset_dir} does not exist.")
        sys.exit(1)
    
    # List available files
    cpp_files = list(dataset_dir.glob("*.cpp"))
    print(f"\nFound {len(cpp_files)} C++ files in dataset:")
    for f in cpp_files:
        print(f"  - {f.name}")
    
    # Create transformer and run
    transformer = PairsTransformer(str(dataset_dir))
    
    try:
        transformed_data = transformer.transform_pairs(str(input_csv), str(output_csv))
        transformer.print_statistics()
        
        print("\n=== Transformation Complete ===")
        print(f"Input: {input_csv}")
        print(f"Output: {output_csv}")
        print(f"Rows: {transformed_data.shape[0]}")
        print(f"Columns: {transformed_data.shape[1]}")
        
    except Exception as e:
        print(f"Error during transformation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
