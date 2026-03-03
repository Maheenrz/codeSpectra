# detectors/type3/training/train_model.py
"""
Offline training script for the Type-3 unified Random Forest model.

Run this directly — it is never imported by the detection runtime.

Usage:
    cd analysis-engine
    python -m detectors.type3.training.train_model

Expects:
    <repo_root>/dsa_dataset/pairs_features.csv

Produces:
    detectors/type3/models/type3_unified_model.joblib
    detectors/type3/models/type3_unified_model.names.json
    detectors/type3/models/type3_unified_model.meta.json
"""

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
import joblib

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parents[4]   # codeSpectra/
DATA_PATH   = REPO_ROOT / "dsa_dataset" / "pairs_features.csv"
OUT_DIR     = Path(__file__).resolve().parents[1] / "models"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH    = OUT_DIR / "type3_unified_model.joblib"
NAMES_PATH    = OUT_DIR / "type3_unified_model.names.json"
META_PATH     = OUT_DIR / "type3_unified_model.meta.json"



# ---------------------------------------------------------------------------
# Load dataset
# ---------------------------------------------------------------------------
def load_dataset(path: Path):
    with path.open("r") as f:
        rows = list(csv.DictReader(f))

    feature_names = [k for k in rows[0].keys() if k != "label"]
    X = np.array(
        [[float(r[fn]) for fn in feature_names] for r in rows],
        dtype=np.float32,
    )
    y = np.array([int(r["label"]) for r in rows], dtype=np.int32)
    return X, y, feature_names


# ---------------------------------------------------------------------------
# Find optimal threshold from probabilities
# ---------------------------------------------------------------------------
def find_optimal_threshold(clf, X_val, y_val):
    from sklearn.metrics import f1_score
    probs = clf.predict_proba(X_val)[:, 1]
    best_t, best_f1 = 0.5, 0.0
    for t in np.arange(0.2, 0.8, 0.02):
        preds = (probs >= t).astype(int)
        f1 = f1_score(y_val, preds, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_t = t
    return float(best_t)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"[INFO] Loading data from: {DATA_PATH}")
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"pairs_features.csv not found at {DATA_PATH}\n"
            "Run tranform_pair_features.py first."
        )

    X, y, feature_names = load_dataset(DATA_PATH)
    print(f"[INFO] Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"[INFO] Label distribution: {dict(zip(*np.unique(y, return_counts=True)))}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Cross-validation
    clf_cv = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        n_jobs=-1,
        class_weight="balanced_subsample",
        random_state=42,
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1 = cross_val_score(clf_cv, X_train, y_train, scoring="f1", cv=cv, n_jobs=-1)
    print(f"[CV]   F1 = {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")

    # Final model
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        n_jobs=-1,
        class_weight="balanced_subsample",
        random_state=42,
    )
    clf.fit(X_train, y_train)

    # Evaluation
    y_pred  = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
    auc     = roc_auc_score(y_test, y_proba)

    print("\n[TEST] Classification report:")
    print(classification_report(y_test, y_pred, digits=4))
    print("[TEST] Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))
    print(f"[TEST] AUC-ROC: {auc:.4f}")

    # Per-language thresholds (approximate based on global optimal)
    base_threshold = find_optimal_threshold(clf, X_test, y_test)
    language_thresholds = {
        "java":       round(base_threshold, 4),
        "cpp":        round(base_threshold - 0.02, 4),
        "c":          round(base_threshold - 0.02, 4),
        "python":     round(base_threshold + 0.02, 4),
        "javascript": round(base_threshold, 4),
    }

    # Save
    joblib.dump(clf, MODEL_PATH)
    NAMES_PATH.write_text(json.dumps(feature_names, indent=2))

    from sklearn.metrics import f1_score
    y_pred_opt = (y_proba >= base_threshold).astype(int)
    test_f1    = f1_score(y_test, y_pred_opt, zero_division=0)

    meta = {
        "model_name":          "type3_unified_model",
        "optimal_threshold":   base_threshold,
        "n_features":          len(feature_names),
        "feature_names":       feature_names,
        "metrics": {
            "cv_f1_mean":         float(cv_f1.mean()),
            "cv_f1_std":          float(cv_f1.std()),
            "test_f1":            float(test_f1),
            "test_auc":           float(auc),
            "optimal_threshold":  base_threshold,
            "train_samples":      int(X_train.shape[0]),
            "test_samples":       int(X_test.shape[0]),
        },
        "language_thresholds": language_thresholds,
    }
    META_PATH.write_text(json.dumps(meta, indent=2))

    print(f"\n[DONE] Saved model    → {MODEL_PATH}")
    print(f"[DONE] Saved features → {NAMES_PATH}")
    print(f"[DONE] Saved metadata → {META_PATH}")
    print(f"[DONE] Optimal threshold: {base_threshold:.4f}")


if __name__ == "__main__":
    main()