# Quick Start Guide

This guide will help you get started with the feature extraction pipeline for ML training.

## Prerequisites

```bash
pip install numpy tree-sitter tree-sitter-cpp tree-sitter-java tree-sitter-python tree-sitter-javascript
```

Optional (for ML training example):
```bash
pip install scikit-learn pandas
```

## Step 1: Prepare Your Dataset

1. Create C++ files in `codespectra/dsa_dataset/`
2. Create a `pairs.csv` file with the following format:

```csv
unitA_id,unitB_id,label
file1.cpp,file2.cpp,1
file1.cpp,file3.cpp,0
...
```

Where:
- `unitA_id`, `unitB_id`: Filenames of C++ files in the dataset
- `label`: 1 for similar/plagiarized code, 0 for different code

## Step 2: Run the Transformation

```bash
cd /path/to/codeSpectra
python3 codespectra/transform_pairs.py
```

This will:
- Process all `.cpp` files referenced in `pairs.csv`
- Extract feature vectors using AST analysis
- Generate `pairs_transformed.csv` with numerical features

## Step 3: Use the Transformed Data

The output `pairs_transformed.csv` has the format:
```
[unitA_feature1, unitA_feature2, ..., unitB_feature1, unitB_feature2, ..., label]
```

### Example: Train a classifier

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load data
df = pd.read_csv('codespectra/dsa_dataset/pairs_transformed.csv')
X = df.iloc[:, :-1].values  # Features
y = df.iloc[:, -1].values   # Labels

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Evaluate
accuracy = clf.score(X_test, y_test)
print(f"Accuracy: {accuracy:.2%}")
```

Or run the provided example:
```bash
python3 codespectra/example_ml_training.py
```

## Feature Vector Details

Each code file is represented by a 16-dimensional feature vector:
- **13 dimensions**: Counts of AST node types (function_definition, for_statement, if_statement, etc.)
- **3 dimensions**: Aggregate metrics (total_nodes, unique_nodes, control_flow_nodes)

The final dataset has 33 columns:
- 16 features for unitA
- 16 features for unitB
- 1 label column

## Programmatic Usage

```python
import sys
sys.path.insert(0, '/path/to/analysis-engine/core')
from ast_ml_adapter import ASTMLAdapter

# Initialize
adapter = ASTMLAdapter()

# Extract features from a file
features = adapter.extract_feature_vector('path/to/file.cpp')
print(f"Features: {features}")

# Get feature names
names = adapter.get_feature_names()
for name, value in zip(names, features):
    print(f"{name}: {value}")

# Batch processing
file_list = ['file1.cpp', 'file2.cpp', 'file3.cpp']
features_matrix = adapter.batch_extract_features(file_list)
print(f"Batch shape: {features_matrix.shape}")
```

## Troubleshooting

### "No module named 'numpy'"
```bash
pip install numpy
```

### "No module named 'tree_sitter'"
```bash
pip install tree-sitter tree-sitter-cpp
```

### "File does not exist"
Check that:
1. Your `.cpp` files are in `codespectra/dsa_dataset/`
2. Filenames in `pairs.csv` match the actual files
3. You're running the script from the repository root

### Empty feature vectors (all zeros)
This means the file couldn't be parsed. Check:
1. File is valid C++ code
2. File extension is `.cpp`, `.c`, `.h`, or `.hpp`
3. File exists and is readable

## Next Steps

1. **Add more samples**: The example dataset is small. Add more C++ files and pairs for better model training.

2. **Experiment with features**: Modify `ASTMLAdapter.extract_feature_vector()` to include additional metrics like:
   - Lines of code
   - Cyclomatic complexity
   - Function count
   - Variable names (hashed)

3. **Try different models**: The example uses Random Forest, but you can try:
   - Support Vector Machines (SVM)
   - Neural Networks
   - XGBoost
   - Logistic Regression

4. **Feature engineering**: Experiment with:
   - Normalized features
   - Feature scaling
   - Dimensionality reduction (PCA)
   - Feature selection

5. **Evaluation**: Use cross-validation and multiple metrics:
   - Precision, Recall, F1-score
   - ROC-AUC
   - Confusion matrix analysis

## Support

For more details, see:
- `codespectra/README.md` - Comprehensive documentation
- `analysis-engine/core/ast_ml_adapter.py` - Source code with docstrings
- `codespectra/test_ast_ml_adapter.py` - Unit tests showing usage examples
