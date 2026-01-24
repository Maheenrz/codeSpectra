import csv
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Set

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    f1_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
import joblib
import json

rng = np.random.default_rng(42)


def resolve_repo_root() -> Path:
    """
    Locate repo root given this file path:
    repo_root/analysis-engine/detectors/type3/model.py
    """
    p = Path(__file__).resolve()
    candidates = []
    try:
        candidates.append(p.parents[3])  # repo_root
    except Exception:
        pass
    try:
        candidates.append(p.parents[2].parent)
    except Exception:
        pass
    candidates.append(Path.cwd().resolve())
    for root in candidates:
        if (root / "dsa_dataset").exists():
            return root
    return candidates[0]


def load_pairs_transformed(csv_path: Path) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Load pairs_transformed.csv where last column is 'label'
    Returns X, y, header (full header list).
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    with csv_path.open("r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    X = np.array([list(map(float, r[:-1])) for r in rows], dtype=np.float32)
    y = np.array([int(r[-1]) for r in rows], dtype=np.int32)
    return X, y, header


def load_pairs_ids(pairs_csv: Path) -> List[Tuple[str, str, int]]:
    """
    Load unit IDs from pairs.csv in the SAME ORDER the transformed CSV was written.
    Returns list of (unitA_id, unitB_id, label).
    """
    if not pairs_csv.exists():
        raise FileNotFoundError(f"pairs.csv not found: {pairs_csv}")
    pairs = []
    with pairs_csv.open("r", newline="") as f:
        reader = csv.reader(f)
        _ = next(reader, None)
        for row in reader:
            if len(row) >= 3:
                ua, ub, lab = row[0], row[1], int(row[2])
                pairs.append((ua, ub, lab))
    return pairs


def make_disjoint_unit_split(
    pairs: List[Tuple[str, str, int]],
    test_size: float = 0.25,
    random_state: int = 42,
) -> Tuple[List[int], List[int]]:
    """
    Split by UNIQUE UNIT IDs so train/test sets are DISJOINT in units.
    We first split unit IDs, then keep only pairs whose BOTH units fall entirely in train or test.
    Returns index lists for train and test pairs (indices into the original order).
    """
    # Collect all unique unit IDs
    units: Set[str] = set()
    for ua, ub, _ in pairs:
        units.add(ua)
        units.add(ub)
    units = list(units)

    # Random split of unit IDs
    rng_local = np.random.default_rng(random_state)
    perm = rng_local.permutation(len(units))
    units = [units[i] for i in perm]

    n_test_units = max(1, int(len(units) * test_size))
    test_units = set(units[:n_test_units])
    train_units = set(units[n_test_units:])

    # Build pair indices ensuring both units fall entirely in one side
    idx_train, idx_test = [], []
    for i, (ua, ub, _) in enumerate(pairs):
        in_train = (ua in train_units) and (ub in train_units)
        in_test = (ua in test_units) and (ub in test_units)
        if in_train:
            idx_train.append(i)
        elif in_test:
            idx_test.append(i)
        # else: pair spans train+test units → drop to avoid leakage

    # If one side is empty, adjust by flipping a few units
    if len(idx_train) == 0 or len(idx_test) == 0:
        move_count = max(1, int(len(test_units) * 0.1))
        moved = 0
        for u in list(test_units):
            if moved >= move_count:
                break
            test_units.remove(u)
            train_units.add(u)
            moved += 1
        idx_train, idx_test = [], []
        for i, (ua, ub, _) in enumerate(pairs):
            in_train = (ua in train_units) and (ub in train_units)
            in_test = (ua in test_units) and (ub in test_units)
            if in_train:
                idx_train.append(i)
            elif in_test:
                idx_test.append(i)

    return idx_train, idx_test


def print_dataset_stats(X: np.ndarray, y: np.ndarray, pairs: List[Tuple[str, str, int]], idx_train: List[int], idx_test: List[int]):
    print(f"[INFO] Samples: {X.shape[0]} | Features: {X.shape[1]}")
    unique, counts = np.unique(y, return_counts=True)
    dist = {int(k): int(v) for k, v in zip(unique, counts)}
    print(f"[INFO] Class distribution (all): {dist}")
    y_tr = np.array([pairs[i][2] for i in idx_train], dtype=np.int32)
    y_te = np.array([pairs[i][2] for i in idx_test], dtype=np.int32)
    ct_tr_0 = int((y_tr == 0).sum())
    ct_tr_1 = int((y_tr == 1).sum())
    ct_te_0 = int((y_te == 0).sum())
    ct_te_1 = int((y_te == 1).sum())
    print(f"[INFO] Train pairs: {len(idx_train)} (0: {ct_tr_0}, 1: {ct_tr_1}) | Test pairs: {len(idx_test)} (0: {ct_te_0}, 1: {ct_te_1})")


def eval_model_disjoint(name: str, pipe: Pipeline, X: np.ndarray, y: np.ndarray, idx_train: List[int], idx_test: List[int]) -> Dict[str, float]:
    print(f"\n===== {name} (Disjoint Units Split) =====")
    X_train, y_train = X[idx_train], y[idx_train]
    X_test, y_test = X[idx_test], y[idx_test]

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    print("[TEST] Classification report:")
    print(classification_report(y_test, y_pred, digits=3))
    print("[TEST] Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    metrics = {
        "f1_macro": f1_score(y_test, y_pred, average="macro"),
        "f1_weighted": f1_score(y_test, y_pred, average="weighted"),
        "accuracy": float((y_pred == y_test).mean()),
    }

    # AUC metrics (if available)
    y_score = None
    if hasattr(pipe[-1], "predict_proba"):
        y_score = pipe.predict_proba(X_test)[:, 1]
    elif hasattr(pipe[-1], "decision_function"):
        y_score = pipe.decision_function(X_test)
    if y_score is not None:
        try:
            metrics["roc_auc"] = roc_auc_score(y_test, y_score)
            metrics["pr_auc"] = average_precision_score(y_test, y_score)
            print(f"[TEST] ROC-AUC: {metrics['roc_auc']:.3f} | PR-AUC: {metrics['pr_auc']:.3f}")
        except Exception:
            pass

    return metrics


def build_pipelines() -> Dict[str, Pipeline]:
    return {
        "LogisticRegression": Pipeline(steps=[
            ("scaler", StandardScaler(with_mean=False)),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ]),
        "LinearSVC": Pipeline(steps=[
            ("scaler", StandardScaler(with_mean=False)),
            ("clf", LinearSVC(class_weight="balanced")),
        ]),
        "RandomForest": Pipeline(steps=[
            ("clf", RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                n_jobs=-1,
                class_weight="balanced_subsample",
                random_state=42
            )),
        ]),
    }


def save_model(pipe: Pipeline, feature_names: List[str], out_dir: Path, name: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / f"{name}.joblib"
    feat_path = out_dir / f"{name}.features.json"
    joblib.dump(pipe, model_path)
    feat_path.write_text(json.dumps(feature_names, indent=2))
    print(f"[INFO] Saved model to: {model_path}")
    print(f"[INFO] Saved feature order to: {feat_path}")


def main():
    repo_root = resolve_repo_root()
    default_csv = repo_root / "dsa_dataset" / "pairs_transformed.csv"
    pairs_csv = repo_root / "dsa_dataset" / "pairs.csv"

    # CLI:
    #   python model.py                 -> evaluate, no save
    #   python model.py save           -> save best-by-macro-F1
    #   python model.py save=rf        -> save RandomForest explicitly
    #   python model.py /path/to.csv   -> use custom csv, evaluate
    #   python model.py /path/to.csv save=rf -> custom csv + save RF
    args = sys.argv[1:]
    save_flag = None
    csv_path = default_csv

    # Parse args
    for a in args:
        if a.startswith("save"):
            save_flag = a  # "save" or "save=rf"/"save=lr"/"save=svm"
        else:
            # Treat as CSV path if not a 'save' flag
            candidate = Path(a).resolve()
            if candidate.exists():
                csv_path = candidate

    print(f"[INFO] Script dir: {Path(__file__).resolve().parent}")
    print(f"[INFO] Repo root:  {repo_root}")
    print(f"[INFO] Using dataset: {csv_path}")

    # Load features and labels
    X, y, header = load_pairs_transformed(csv_path)
    feature_names = [h for h in header if h != "label"]

    # Load unit IDs (must be aligned with pairs_transformed row order)
    pairs = load_pairs_ids(pairs_csv)
    if len(pairs) != X.shape[0]:
        print(f"[WARN] pairs.csv count ({len(pairs)}) != transformed rows ({X.shape[0]}). "
              f"Ensure transform script writes rows in the same order as pairs.csv.")
        # Proceed anyway.

    # Build disjoint unit split
    idx_train, idx_test = make_disjoint_unit_split(pairs, test_size=0.25, random_state=42)
    if len(idx_train) == 0 or len(idx_test) == 0:
        raise RuntimeError("Disjoint unit split failed: empty train or test. Try adjusting test_size or random_state.")

    print_dataset_stats(X, y, pairs, idx_train, idx_test)
    print(f"[INFO] Header sample: {header[:6]} ... [label at the end: {header[-1]}]")

    # Evaluate models
    pipes = build_pipelines()
    results = {}
    for name, pipe in pipes.items():
        metrics = eval_model_disjoint(name, pipe, X, y, idx_train, idx_test)
        results[name] = metrics

    # Decide which model to save
    models_dir = Path(__file__).resolve().parent / "models"
    target_name = None

    if save_flag is None:
        print("\n[INFO] No save flag provided. Done.")
        return

    if save_flag == "save":
        # Save best by macro F1
        target_name = max(results.keys(), key=lambda k: results[k].get("f1_macro", 0.0))
    elif save_flag.startswith("save="):
        opt = save_flag.split("=", 1)[1].strip().lower()
        mapping = {"rf": "RandomForest", "randomforest": "RandomForest",
                   "lr": "LogisticRegression", "logistic": "LogisticRegression",
                   "svm": "LinearSVC", "linearsvc": "LinearSVC"}
        target_name = mapping.get(opt)
        if target_name is None:
            print(f"[WARN] Unknown save option '{opt}'. Falling back to best-by-macro-F1.")
            target_name = max(results.keys(), key=lambda k: results[k].get("f1_macro", 0.0))
    else:
        # Default: best-by-macro-F1
        target_name = max(results.keys(), key=lambda k: results[k].get("f1_macro", 0.0))

    # Refit the selected model on the FULL TRAIN SPLIT and save
    pipe = pipes[target_name]
    X_train, y_train = X[idx_train], y[idx_train]
    pipe.fit(X_train, y_train)
    save_model(pipe, feature_names, models_dir, f"type3_{target_name.lower()}")

    print(f"[INFO] Saved '{target_name}' as the deployed model.")
    print("[INFO] Done.")


if __name__ == "__main__":
    main()