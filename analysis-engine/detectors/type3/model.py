import csv
import json
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Repo root = three levels above detectors/type3 (codeSpectra/)
# .../analysis-engine/detectors/type3/model.py -> parents[3] == repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA = REPO_ROOT / "dsa_dataset" / "pairs_features.csv"

OUT_DIR = Path(__file__).resolve().parent / "models"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = OUT_DIR / "type3_rf_features.joblib"
FEATURES_PATH = OUT_DIR / "type3_rf_features.names.json"

def load_dataset(path: Path):
    with path.open("r") as f:
        rows = list(csv.DictReader(f))
    feature_names = [fn for fn in rows[0].keys() if fn != "label"]
    X = np.array([[float(r[fn]) for fn in feature_names] for r in rows], dtype=np.float32)
    y = np.array([int(r["label"]) for r in rows], dtype=np.int32)
    return X, y, feature_names

def main():
    print(f"[DEBUG] Looking for pairs_features at: {DATA}")
    if not DATA.exists():
        raise FileNotFoundError(
            f"pairs_features.csv not found: {DATA}\n"
            f"Make sure you ran transform_pair_features.py and that dsa_dataset is at {REPO_ROOT / 'dsa_dataset'}"
        )

    X, y, feature_names = load_dataset(DATA)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        n_jobs=-1,
        class_weight="balanced_subsample",
        random_state=42,
    )
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("[TEST] Classification report:")
    print(classification_report(y_test, y_pred, digits=3))
    print("[TEST] Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    joblib.dump(clf, MODEL_PATH)
    FEATURES_PATH.write_text(json.dumps(feature_names, indent=2))
    print(f"[INFO] Saved model: {MODEL_PATH}")
    print(f"[INFO] Saved feature order: {FEATURES_PATH}")

if __name__ == "__main__":
    main()