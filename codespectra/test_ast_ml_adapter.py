#!/usr/bin/env python3
"""
test_ast_ml_adapter.py

Unit tests for ASTMLAdapter functionality.
"""

import sys
import os
from pathlib import Path

# Add analysis-engine/core to path
script_dir = Path(__file__).parent.absolute()
core_dir = script_dir.parent / "analysis-engine" / "core"
sys.path.insert(0, str(core_dir))

from ast_ml_adapter import ASTMLAdapter
import numpy as np


def test_initialization():
    """Test ASTMLAdapter initialization."""
    print("Testing ASTMLAdapter initialization...")
    adapter = ASTMLAdapter()
    assert adapter is not None
    assert hasattr(adapter, 'ast_processor')
    assert hasattr(adapter, 'node_types')
    print("✓ Initialization test passed")


def test_feature_names():
    """Test feature names retrieval."""
    print("Testing feature names...")
    adapter = ASTMLAdapter()
    feature_names = adapter.get_feature_names()
    assert isinstance(feature_names, list)
    assert len(feature_names) == 16  # 13 node types + 3 aggregate metrics
    assert 'function_definition' in feature_names
    assert 'total_nodes' in feature_names
    assert 'control_flow_nodes' in feature_names
    print(f"✓ Feature names test passed ({len(feature_names)} features)")


def test_extract_features():
    """Test feature extraction from actual C++ files."""
    print("Testing feature extraction...")
    adapter = ASTMLAdapter()
    
    # Test with binary_search.cpp
    dataset_dir = script_dir / "dsa_dataset"
    test_file = dataset_dir / "binary_search.cpp"
    
    if not test_file.exists():
        print(f"⚠ Warning: Test file {test_file} not found, skipping test")
        return
    
    features = adapter.extract_feature_vector(str(test_file))
    
    assert isinstance(features, np.ndarray)
    assert len(features) == 16
    assert features.dtype == np.float32
    
    # Check that at least some features are non-zero
    assert np.count_nonzero(features) > 0
    
    print(f"✓ Feature extraction test passed")
    print(f"  Feature vector shape: {features.shape}")
    print(f"  Non-zero elements: {np.count_nonzero(features)}")
    print(f"  Sum: {np.sum(features):.2f}")


def test_normalize_code():
    """Test code normalization."""
    print("Testing code normalization...")
    adapter = ASTMLAdapter()
    
    dataset_dir = script_dir / "dsa_dataset"
    test_file = dataset_dir / "binary_search.cpp"
    
    if not test_file.exists():
        print(f"⚠ Warning: Test file {test_file} not found, skipping test")
        return
    
    normalized = adapter.normalize_code(str(test_file))
    
    assert isinstance(normalized, str)
    assert len(normalized) > 0
    
    # Should contain some structural keywords
    assert any(keyword in normalized for keyword in ['function_definition', 'while_statement', 'if_statement', 'return_statement'])
    
    print(f"✓ Code normalization test passed")
    print(f"  Normalized sequence length: {len(normalized)}")
    print(f"  Sample: {normalized[:100]}...")


def test_batch_extraction():
    """Test batch feature extraction."""
    print("Testing batch feature extraction...")
    adapter = ASTMLAdapter()
    
    dataset_dir = script_dir / "dsa_dataset"
    test_files = [
        dataset_dir / "binary_search.cpp",
        dataset_dir / "bubble_sort.cpp",
    ]
    
    # Filter to existing files
    existing_files = [str(f) for f in test_files if f.exists()]
    
    if len(existing_files) < 2:
        print(f"⚠ Warning: Not enough test files found, skipping test")
        return
    
    features_matrix = adapter.batch_extract_features(existing_files)
    
    assert isinstance(features_matrix, np.ndarray)
    assert features_matrix.shape[0] == len(existing_files)
    assert features_matrix.shape[1] == 16
    
    print(f"✓ Batch extraction test passed")
    print(f"  Batch shape: {features_matrix.shape}")


def test_similarity_detection():
    """Test that similar files produce similar features."""
    print("Testing similarity detection...")
    adapter = ASTMLAdapter()
    
    dataset_dir = script_dir / "dsa_dataset"
    file1 = dataset_dir / "binary_search.cpp"
    file2 = dataset_dir / "binary_search_variant.cpp"
    file3 = dataset_dir / "bubble_sort.cpp"
    
    if not all([file1.exists(), file2.exists(), file3.exists()]):
        print(f"⚠ Warning: Test files not found, skipping test")
        return
    
    features1 = adapter.extract_feature_vector(str(file1))
    features2 = adapter.extract_feature_vector(str(file2))
    features3 = adapter.extract_feature_vector(str(file3))
    
    # Calculate cosine similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_12 = cosine_similarity(features1, features2)  # Similar files
    sim_13 = cosine_similarity(features1, features3)  # Different files
    
    print(f"  Similarity (binary_search vs variant): {sim_12:.4f}")
    print(f"  Similarity (binary_search vs bubble_sort): {sim_13:.4f}")
    
    # Similar files should have higher similarity
    assert sim_12 > sim_13, "Similar files should have higher similarity"
    
    print(f"✓ Similarity detection test passed")


def test_metadata_extraction():
    """Test feature extraction with metadata."""
    print("Testing metadata extraction...")
    adapter = ASTMLAdapter()
    
    dataset_dir = script_dir / "dsa_dataset"
    test_file = dataset_dir / "binary_search.cpp"
    
    if not test_file.exists():
        print(f"⚠ Warning: Test file {test_file} not found, skipping test")
        return
    
    metadata = adapter.extract_features_with_metadata(str(test_file))
    
    assert isinstance(metadata, dict)
    assert 'file_path' in metadata
    assert 'features' in metadata
    assert 'feature_names' in metadata
    assert 'structure_sequence' in metadata
    assert 'feature_dimension' in metadata
    
    assert metadata['feature_dimension'] == 16
    
    print(f"✓ Metadata extraction test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running ASTMLAdapter Tests")
    print("=" * 60)
    
    tests = [
        test_initialization,
        test_feature_names,
        test_extract_features,
        test_normalize_code,
        test_batch_extraction,
        test_similarity_detection,
        test_metadata_extraction,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print()
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
