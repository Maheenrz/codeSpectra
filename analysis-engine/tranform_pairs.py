import os
import csv
import numpy as np
from pathlib import Path
from core.ast_ml_adapter import ASTMLAdapter
from typing import List, Tuple, Dict
import sys
import os
sys.path.insert(0, os.path.abspath("."))  # Add the current directory to PYTHONPATH

# Base Paths
DSA_DATASET_PATH = "dsa_dataset"  # Path to your dataset folder
OUTPUT_CSV = os.path.join(DSA_DATASET_PATH, "pairs_transformed.csv")  # Output CSV location
PAIRS_CSV = os.path.join(DSA_DATASET_PATH, "pairs.csv")  # Path to current pairs.csv
CACHE_DIR = "feature_cache"  # Directory for cached features

# Initialize the ASTMLAdapter
ast_adapter = ASTMLAdapter(cache_dir=os.path.join("analysis-engine", CACHE_DIR))


def get_cpp_files_from_dataset(base_dir: str) -> List[Path]:
    """
    Recursively find all .cpp files in the dataset folder.
    """
    cpp_files = []
    dataset_root = Path(base_dir)
    for filepath in dataset_root.rglob("*.cpp"):
        cpp_files.append(filepath)
    return cpp_files


def process_cpp_files(cpp_files: List[Path]) -> Dict[str, np.ndarray]:
    """
    Process each .cpp file, build units with ASTMLAdapter, and generate feature vectors.
    
    Returns a mapping of unit IDs to their feature vectors.
    """
    unit_vector_map = {}
    for cpp_file in cpp_files:
        print(f"Processing: {cpp_file}")
        
        # Build Units from file
        units = ast_adapter.build_units_from_file(str(cpp_file))
        
        # Normalize and vectorize each unit
        for unit in units:
            ast_adapter.normalize_unit(unit)
            ast_adapter.compute_subtree_hashes(unit)
            ast_adapter.extract_ast_paths(unit)
            ast_adapter.compute_ast_counts(unit)
            vector = ast_adapter.vectorize_units([unit])[0][0]
            unit_vector_map[unit.id] = vector
    
    print(f"Processed {len(unit_vector_map)} units from {len(cpp_files)} files.")
    return unit_vector_map


def transform_pairs_to_vector(pairs_csv: str, unit_vector_map: Dict[str, np.ndarray], output_csv: str):
    """
    Transform pairs.csv to a new CSV with feature vectors.
    """
    if not os.path.exists(pairs_csv):
        raise FileNotFoundError(f"pairs.csv not found at {pairs_csv}")

    pairs = []
    with open(pairs_csv, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)  # Skip header
        for row in reader:
            pairs.append(row)

    processed = []
    for pair in pairs:
        unit_a_id, unit_b_id, label = pair
        vector_a = unit_vector_map.get(unit_a_id)
        vector_b = unit_vector_map.get(unit_b_id)
        
        if vector_a is None or vector_b is None:
            print(f"Warning: Missing vector for {unit_a_id} or {unit_b_id}. Skipping...")
            continue
        
        # Combine feature vectors of Unit A and Unit B (stacking horizontally)
        combined_vector = list(vector_a) + list(vector_b) + [int(label)]
        processed.append(combined_vector)

    # Write processed pairs to a new CSV file
    feature_length = len(next(iter(unit_vector_map.values())))
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        # Dynamic header generation
        feature_headers = [f"a_f{i}" for i in range(feature_length)] + [f"b_f{i}" for i in range(feature_length)] + ["label"]
        writer.writerow(feature_headers)
        writer.writerows(processed)
    
    print(f"Saved transformed pairs to: {output_csv}")


def main():
    # Step 1: Extract all .cpp files in dataset
    cpp_files = get_cpp_files_from_dataset(DSA_DATASET_PATH)
    if not cpp_files:
        print(f"No .cpp files found in {DSA_DATASET_PATH}. Exiting...")
        return

    # Step 2: Process these files and generate feature vectors
    unit_vector_map = process_cpp_files(cpp_files)

    # Step 3: Transform pairs.csv into machine learning ready CSV
    transform_pairs_to_vector(PAIRS_CSV, unit_vector_map, OUTPUT_CSV)


if __name__ == "__main__":
    main()