# DSA Dataset Feature Extraction

This directory contains the DSA (Data Structures and Algorithms) dataset and the automated feature extraction pipeline for ML model training.

## Directory Structure

```
codespectra/
├── dsa_dataset/              # Dataset directory
│   ├── *.cpp                 # C++ source files
│   ├── pairs.csv             # Original pairs with symbolic IDs
│   └── pairs_transformed.csv # Transformed pairs with feature vectors
└── transform_pairs.py        # Transformation script
```

## Components

### 1. ASTMLAdapter (`analysis-engine/core/ast_ml_adapter.py`)

The `ASTMLAdapter` class provides ML-ready feature extraction from AST representations:

- **normalize_code(file_path)**: Extracts structural skeleton from code
- **extract_feature_vector(file_path)**: Generates numerical feature vector
- **batch_extract_features(file_paths)**: Processes multiple files
- **get_feature_names()**: Returns feature dimension names

#### Feature Vector Composition

Each feature vector contains 16 dimensions:
1. **Node Type Counts** (13 dimensions): Frequency of each AST node type:
   - function_definition, method_declaration
   - for_statement, while_statement, do_statement
   - if_statement, else_clause
   - try_statement, catch_clause
   - switch_statement, case_statement
   - return_statement, class_definition

2. **Aggregate Metrics** (3 dimensions):
   - total_nodes: Total number of structural nodes
   - unique_nodes: Number of unique node types
   - control_flow_nodes: Count of control flow structures

### 2. Dataset (`dsa_dataset/`)

Sample C++ implementations of common algorithms:
- `binary_search.cpp` - Binary search implementation
- `binary_search_variant.cpp` - Similar implementation (positive pair)
- `bubble_sort.cpp` - Bubble sort algorithm
- `quick_sort.cpp` - Quick sort algorithm
- `linear_search.cpp` - Linear search implementation

### 3. Pairs File Format

#### `pairs.csv` (Input)
```csv
unitA_id,unitB_id,label
binary_search.cpp,binary_search_variant.cpp,1
binary_search.cpp,bubble_sort.cpp,0
...
```

#### `pairs_transformed.csv` (Output)
```csv
unitA_feature1,unitA_feature2,...,unitB_feature1,unitB_feature2,...,label
2.0,0.0,0.0,1.0,...,2.0,0.0,0.0,1.0,...,1.0
...
```

**Format**: Each row contains `[unitA_features (16 dims), unitB_features (16 dims), label (1 dim)]` = **33 total columns**

## Usage

### Basic Usage

```bash
cd /path/to/codeSpectra
python3 codespectra/transform_pairs.py
```

This will:
1. Read `pairs.csv` from `dsa_dataset/`
2. Process each referenced C++ file
3. Extract feature vectors using ASTMLAdapter
4. Generate `pairs_transformed.csv` with numerical features

### Expected Output

```
=== DSA Dataset Pairs Transformation ===
Found 5 C++ files in dataset:
  - binary_search.cpp
  - binary_search_variant.cpp
  - bubble_sort.cpp
  - quick_sort.cpp
  - linear_search.cpp

Processing pair 1/9: binary_search.cpp vs binary_search_variant.cpp
...

=== Transformation Complete ===
Output shape: (9, 33)
Features per unit: 16
Total columns: 33
```

### Programmatic Usage

```python
import sys
sys.path.insert(0, '/path/to/analysis-engine/core')
from ast_ml_adapter import ASTMLAdapter

# Initialize adapter
adapter = ASTMLAdapter()

# Extract features from a single file
features = adapter.extract_feature_vector('path/to/file.cpp')
print(f"Feature vector: {features}")
print(f"Dimensions: {len(features)}")

# Get feature names
feature_names = adapter.get_feature_names()
print(f"Features: {feature_names}")

# Batch processing
file_paths = ['file1.cpp', 'file2.cpp', 'file3.cpp']
features_matrix = adapter.batch_extract_features(file_paths)
print(f"Batch shape: {features_matrix.shape}")
```

## Requirements

The transformation script requires the following Python packages:
- `numpy` - Numerical operations
- `tree-sitter` - AST parsing
- `tree-sitter-cpp` - C++ language support
- `tree-sitter-java` - Java language support (for ASTProcessor)
- `tree-sitter-python` - Python language support (for ASTProcessor)
- `tree-sitter-javascript` - JavaScript language support (for ASTProcessor)

These are already listed in `analysis-engine/requirements.txt`.

## Integration with Existing Code

The `ASTMLAdapter` integrates with:
- **ASTProcessor** (`analysis-engine/core/ast_processor.py`): Uses tree-sitter for AST parsing
- **Existing detectors**: Can be used alongside Type 1-4 clone detection

## ML Model Training

The transformed dataset is ready for ML model training:

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load transformed data
df = pd.read_csv('codespectra/dsa_dataset/pairs_transformed.csv')

# Split features and labels
X = df.iloc[:, :-1].values  # All columns except last (label)
y = df.iloc[:, -1].values   # Last column (label)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train a classifier
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Evaluate
accuracy = clf.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.2f}")
```

## Adding New Files to Dataset

1. Add your `.cpp` files to `dsa_dataset/`
2. Update `pairs.csv` with new pairs:
   ```csv
   unitA_id,unitB_id,label
   new_file.cpp,existing_file.cpp,0
   ```
3. Run `python3 codespectra/transform_pairs.py`
4. The transformed CSV will be automatically updated

## Feature Engineering

You can extend the feature set by modifying `ASTMLAdapter.extract_feature_vector()`:
- Add more AST node types
- Include additional metrics (LOC, complexity)
- Normalize features differently
- Add n-gram features from the structure sequence

## Troubleshooting

### Import Errors
If you encounter import errors, ensure you're in the correct directory:
```bash
cd /path/to/codeSpectra
python3 codespectra/transform_pairs.py
```

### Missing Dependencies
Install required packages:
```bash
pip install numpy tree-sitter tree-sitter-cpp tree-sitter-java tree-sitter-python tree-sitter-javascript
```

### Empty Feature Vectors
If a file returns all zeros, check:
- File exists and is readable
- File extension is supported (.cpp, .c, .h, .hpp)
- File contains valid C++ code that can be parsed

## Notes

- The feature extraction is deterministic and repeatable
- Features are cached during transformation to avoid reprocessing
- The script supports any number of pairs and files
- Labels: 1 = similar/plagiarized, 0 = different/original
