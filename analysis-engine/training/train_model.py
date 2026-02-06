# analysis-engine/training/train_model.py

"""
Train the unified clone detection model.
"""

import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    f1_score
)
import joblib

# Add parent to path
TRAINING_DIR = Path(__file__).resolve().parent
ENGINE_DIR = TRAINING_DIR.parent
sys.path.insert(0, str(ENGINE_DIR))


class CloneDetectorTrainer:
    """Train the unified clone detection model"""
    
    def __init__(self):
        self.models_dir = ENGINE_DIR / "detectors" / "type3" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_dir = ENGINE_DIR / "data" / "features"
    
    def load_features(self, features_path: str = None) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Load features from CSV"""
        
        if features_path is None:
            features_path = self.data_dir / "features.csv"
        else:
            features_path = Path(features_path)
        
        if not features_path.exists():
            print(f"❌ Features not found: {features_path}")
            print("   Run extract_features.py first!")
            sys.exit(1)
        
        print(f"📂 Loading features from: {features_path}")
        df = pd.read_csv(features_path)
        
        feature_names = [col for col in df.columns if col != 'label']
        X = df[feature_names].values.astype(np.float32)
        y = df['label'].values.astype(np.int32)
        
        print(f"   Loaded {X.shape[0]} samples with {X.shape[1]} features")
        
        return X, y, feature_names
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str]
    ) -> Tuple[RandomForestClassifier, float, Dict]:
        """
        Train RandomForest model with evaluation.
        
        Returns:
            model, optimal_threshold, metrics_dict
        """
        
        print("\n" + "=" * 60)
        print("🎯 TRAINING CLONE DETECTION MODEL")
        print("=" * 60)
        
        # Split data (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=0.2, 
            random_state=42, 
            stratify=y
        )
        
        print(f"\n📊 Data Split:")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test:  {len(X_test)} samples")
        print(f"   Train distribution: {np.bincount(y_train).tolist()}")
        print(f"   Test distribution:  {np.bincount(y_test).tolist()}")
        
        # Create model
        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            class_weight='balanced_subsample',
            n_jobs=-1,
            random_state=42,
            verbose=0
        )
        
        # Cross-validation
        print(f"\n🔄 5-Fold Cross-Validation...")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1')
        print(f"   CV F1 Scores: {cv_scores.round(4).tolist()}")
        print(f"   CV Mean F1:   {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
        
        # Train final model
        print(f"\n🎯 Training Final Model...")
        model.fit(X_train, y_train)
        
        # Evaluate on test set
        print(f"\n📈 Test Set Evaluation:")
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        print("\n   Classification Report:")
        report = classification_report(y_test, y_pred, digits=4)
        print("   " + report.replace("\n", "\n   "))
        
        print("\n   Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"   {cm}")
        
        # AUC Score
        auc = roc_auc_score(y_test, y_proba)
        print(f"\n   ROC-AUC Score: {auc:.4f}")
        
        # Find optimal threshold
        precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
        f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
        optimal_idx = np.argmax(f1_scores[:-1])
        optimal_threshold = float(thresholds[optimal_idx])
        
        print(f"\n🎯 Optimal Threshold Analysis:")
        print(f"   Optimal threshold: {optimal_threshold:.4f}")
        print(f"   F1 at optimal:     {f1_scores[optimal_idx]:.4f}")
        print(f"   Precision:         {precisions[optimal_idx]:.4f}")
        print(f"   Recall:            {recalls[optimal_idx]:.4f}")
        
        # Feature importance
        print(f"\n📊 Feature Importance:")
        importances = model.feature_importances_
        for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
            bar = "█" * int(imp * 50)
            print(f"   {name:25s} {imp:.4f} {bar}")
        
        # Compile metrics
        metrics = {
            'cv_f1_mean': float(cv_scores.mean()),
            'cv_f1_std': float(cv_scores.std()),
            'test_f1': float(f1_score(y_test, y_pred)),
            'test_auc': float(auc),
            'optimal_threshold': optimal_threshold,
            'train_samples': int(len(X_train)),
            'test_samples': int(len(X_test)),
        }
        
        return model, optimal_threshold, metrics
    
    def save_model(
        self,
        model: RandomForestClassifier,
        feature_names: List[str],
        optimal_threshold: float,
        metrics: Dict,
        model_name: str = "type3_unified_model"
    ):
        """Save trained model and metadata"""
        
        print("\n" + "=" * 60)
        print("💾 SAVING MODEL")
        print("=" * 60)
        
        # Save model
        model_path = self.models_dir / f"{model_name}.joblib"
        joblib.dump(model, model_path)
        print(f"   Model: {model_path}")
        
        # Save feature names (CRITICAL - must match inference!)
        names_path = self.models_dir / f"{model_name}.names.json"
        with open(names_path, 'w') as f:
            json.dump(feature_names, f, indent=2)
        print(f"   Feature names: {names_path}")
        
        # Save metadata
        meta = {
            'model_name': model_name,
            'optimal_threshold': optimal_threshold,
            'n_features': len(feature_names),
            'feature_names': feature_names,
            'metrics': metrics,
            'language_thresholds': {
                'java': optimal_threshold,
                'cpp': optimal_threshold - 0.02,  # Slightly lower for C++
                'c': optimal_threshold - 0.02,
                'python': optimal_threshold + 0.02,  # Slightly higher for Python
            }
        }
        
        meta_path = self.models_dir / f"{model_name}.meta.json"
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        print(f"   Metadata: {meta_path}")
        
        print(f"\n✅ Model saved successfully!")
        print(f"   Location: {self.models_dir}")


def main():
    """Main training function"""
    
    trainer = CloneDetectorTrainer()
    
    # Load features
    X, y, feature_names = trainer.load_features()
    
    # Train model
    model, optimal_threshold, metrics = trainer.train(X, y, feature_names)
    
    # Save model
    trainer.save_model(model, feature_names, optimal_threshold, metrics)
    
    print("\n" + "=" * 60)
    print("🎉 TRAINING COMPLETE!")
    print("=" * 60)
    print(f"\n📋 Summary:")
    print(f"   Test F1 Score: {metrics['test_f1']:.4f}")
    print(f"   Test AUC:      {metrics['test_auc']:.4f}")
    print(f"   Threshold:     {optimal_threshold:.4f}")
    print(f"\n   Model ready for use in hybrid_detector.py!")


if __name__ == "__main__":
    main()