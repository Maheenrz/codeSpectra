#!/usr/bin/env python3
"""
example_ml_training.py

Example script demonstrating how to use the transformed dataset
for machine learning model training and evaluation.

This script shows:
1. Loading the transformed dataset
2. Splitting into train/test sets
3. Training a classifier
4. Evaluating model performance
"""

import sys
from pathlib import Path

# This is an example - actual usage may require installation of scikit-learn
try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
except ImportError as e:
    print(f"Error: This example requires scikit-learn and pandas.")
    print(f"Install with: pip install scikit-learn pandas")
    print(f"Missing module: {e}")
    sys.exit(1)


def load_transformed_data(csv_path):
    """
    Load the transformed pairs dataset.
    
    Args:
        csv_path: Path to pairs_transformed.csv
        
    Returns:
        X: Feature matrix (n_samples, n_features)
        y: Labels (n_samples,)
    """
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Split features and labels
    # All columns except last are features, last column is label
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    
    print(f"  Loaded {X.shape[0]} samples with {X.shape[1]} features")
    print(f"  Label distribution: {dict(zip(*np.unique(y, return_counts=True)))}")
    
    return X, y


def train_and_evaluate_model(X, y, test_size=0.3, random_state=42):
    """
    Train a classifier and evaluate its performance.
    
    Args:
        X: Feature matrix
        y: Labels
        test_size: Fraction of data to use for testing
        random_state: Random seed for reproducibility
    """
    print(f"\nSplitting data (train={1-test_size:.1%}, test={test_size:.1%})...")
    
    # Check if we have enough samples for stratified split
    unique, counts = np.unique(y, return_counts=True)
    min_class_count = counts.min()
    
    if min_class_count < 2:
        print(f"  Warning: Some classes have only {min_class_count} sample(s). Cannot stratify.")
        print(f"  Using random split instead.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
    
    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Test set: {X_test.shape[0]} samples")
    
    # Train a Random Forest classifier
    print("\nTraining Random Forest classifier...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=random_state
    )
    clf.fit(X_train, y_train)
    
    # Make predictions
    print("Making predictions...")
    y_pred_train = clf.predict(X_train)
    y_pred_test = clf.predict(X_test)
    
    # Calculate metrics
    print("\n" + "=" * 60)
    print("Model Performance Metrics")
    print("=" * 60)
    
    # Training metrics
    train_acc = accuracy_score(y_train, y_pred_train)
    print(f"\nTraining Set:")
    print(f"  Accuracy: {train_acc:.4f}")
    
    # Test metrics
    test_acc = accuracy_score(y_test, y_pred_test)
    test_prec = precision_score(y_test, y_pred_test, zero_division=0)
    test_rec = recall_score(y_test, y_pred_test, zero_division=0)
    test_f1 = f1_score(y_test, y_pred_test, zero_division=0)
    
    print(f"\nTest Set:")
    print(f"  Accuracy:  {test_acc:.4f}")
    print(f"  Precision: {test_prec:.4f}")
    print(f"  Recall:    {test_rec:.4f}")
    print(f"  F1 Score:  {test_f1:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred_test)
    print(f"\nConfusion Matrix:")
    print(f"  {cm}")
    print(f"  (TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]})")
    
    # Feature importance
    print(f"\nTop 10 Most Important Features:")
    feature_importance = clf.feature_importances_
    top_indices = np.argsort(feature_importance)[-10:][::-1]
    for i, idx in enumerate(top_indices, 1):
        print(f"  {i}. Feature {idx}: {feature_importance[idx]:.4f}")
    
    return clf, (train_acc, test_acc, test_prec, test_rec, test_f1)


def cross_validate_model(X, y, n_splits=5):
    """
    Perform cross-validation to get more robust performance estimates.
    
    Args:
        X: Feature matrix
        y: Labels
        n_splits: Number of folds for cross-validation
    """
    from sklearn.model_selection import cross_val_score
    
    print(f"\nPerforming {n_splits}-fold cross-validation...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    
    scores = cross_val_score(clf, X, y, cv=n_splits, scoring='accuracy')
    
    print(f"  Cross-validation scores: {scores}")
    print(f"  Mean accuracy: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")


def main():
    """Main function to run the example."""
    print("=" * 60)
    print("ML Training Example - Code Clone Detection")
    print("=" * 60)
    
    # Determine path to transformed data
    script_dir = Path(__file__).parent.absolute()
    data_path = script_dir / "dsa_dataset" / "pairs_transformed.csv"
    
    if not data_path.exists():
        print(f"Error: Transformed data not found at {data_path}")
        print("Please run transform_pairs.py first to generate the data.")
        sys.exit(1)
    
    # Load data
    X, y = load_transformed_data(data_path)
    
    # Check if we have enough samples
    if len(X) < 5:
        print("\nWarning: Dataset is very small. Results may not be meaningful.")
        print("Consider adding more sample pairs to improve model training.")
    
    # Train and evaluate
    try:
        clf, metrics = train_and_evaluate_model(X, y)
        
        # Cross-validation if we have enough samples
        if len(X) >= 5:
            cross_validate_model(X, y)
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print(f"\nTest Accuracy: {metrics[1]:.2%}")
        print("\nNote: This is a small example dataset.")
        print("For production use, collect more diverse code samples.")
        
    except ValueError as e:
        print(f"\nError during training: {e}")
        print("This may occur if the dataset is too small or imbalanced.")
        print("Try adding more samples or adjusting the test_size parameter.")


if __name__ == "__main__":
    main()
