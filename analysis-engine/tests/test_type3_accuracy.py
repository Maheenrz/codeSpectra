# analysis-engine/tests/test_type3_accuracy.py
"""
End-to-end accuracy test for the Type-3 detector.

Run from analysis-engine/:
    python -m tests.test_type3_accuracy
"""

import csv
import sys
import time
from pathlib import Path
from typing import Optional, List, Tuple

# ── Path setup ────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parents[2]
ENGINE_ROOT = REPO_ROOT / "analysis-engine"
DSA_ROOT    = REPO_ROOT / "dsa_dataset"
PAIRS_CSV   = DSA_ROOT / "pairs.csv"

sys.path.insert(0, str(ENGINE_ROOT))

from detectors.type3.hybrid_detector import Type3HybridDetector


# ── Load ground truth ─────────────────────────────────────────────────────────

def load_pairs() -> List[Tuple[str, str, int]]:
    pairs = []
    with open(PAIRS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label  = int(row["label"])
            file_a = _resolve_path(row["unitA_id"])
            file_b = _resolve_path(row["unitB_id"])
            if file_a and file_b:
                pairs.append((str(file_a), str(file_b), label))
    return pairs


def _resolve_path(unit_id: str) -> Optional[Path]:
    """
    unit_id format:  <filename>:<function_name>
    filename format: <problem>_student<N>[_clone<N>].cpp
    """
    filename = unit_id.split(":")[0]
    if "_student" not in filename:
        return None
    problem = filename.split("_student")[0]
    path = DSA_ROOT / problem / filename
    return path if path.exists() else None


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    print("\n" + "=" * 60)
    print("  Type-3 Detector — End-to-End Accuracy Test")
    print("=" * 60)

    pairs = load_pairs()
    if not pairs:
        print("❌  No pairs loaded. Check dsa_dataset/pairs.csv and file paths.")
        return

    n_clones    = sum(1 for _, _, l in pairs if l == 1)
    n_nonclones = sum(1 for _, _, l in pairs if l == 0)
    print(f"✅  Loaded {len(pairs)} pairs")
    print(f"    Clones     (label=1): {n_clones}")
    print(f"    Non-clones (label=0): {n_nonclones}\n")

    # Prepare detector — batch frequency filter trained on all files
    detector  = Type3HybridDetector()
    all_files = list({f for f, _, _ in pairs} | {f for _, f, _ in pairs})
    detector.prepare_batch([Path(p) for p in all_files])

    y_true: List[int]   = []
    y_pred: List[int]   = []
    y_scores: List[float] = []
    errors = 0
    start  = time.time()

    for i, (fa, fb, label) in enumerate(pairs):
        try:
            result = detector.detect(fa, fb)
            score  = result["combined"]["score"]
            pred   = 1 if result["is_clone"] else 0
            y_true.append(label)
            y_pred.append(pred)
            y_scores.append(score)
        except Exception as e:
            errors += 1
            print(f"  ⚠️  Pair {i}: {Path(fa).name} vs {Path(fb).name} → {e}")

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(pairs)}] {time.time()-start:.1f}s elapsed …")

    elapsed = time.time() - start
    print(f"\n⏱  Done: {len(y_true)} pairs in {elapsed:.1f}s  ({errors} errors skipped)\n")

    _print_metrics(y_true, y_pred, y_scores)
    _print_samples(pairs, y_true, y_pred, y_scores)


def _print_metrics(y_true, y_pred, y_scores):
    try:
        from sklearn.metrics import (
            classification_report, confusion_matrix,
            roc_auc_score, f1_score
        )
        import numpy as np
    except ImportError:
        print("⚠️  sklearn not installed — run: pip install scikit-learn")
        _manual_metrics(y_true, y_pred)
        return

    print("-" * 60)
    print("CONFUSION MATRIX")
    print("-" * 60)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    print(f"               Predicted 0   Predicted 1")
    print(f"  Actual 0     {tn:>10}    {fp:>10}   (TrueNeg / FalsePos)")
    print(f"  Actual 1     {fn:>10}    {tp:>10}   (FalseNeg / TruePos)")
    print()

    print("-" * 60)
    print("CLASSIFICATION REPORT")
    print("-" * 60)
    print(classification_report(
        y_true, y_pred,
        target_names=["Non-Clone", "Clone"],
        digits=4
    ))

    try:
        auc = roc_auc_score(y_true, y_scores)
        print(f"AUC-ROC:  {auc:.4f}")
    except Exception:
        pass

    acc = sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true)
    f1  = f1_score(y_true, y_pred, zero_division=0)
    print(f"Accuracy: {acc:.4f}  ({acc * 100:.1f}%)")
    print(f"F1 Score: {f1:.4f}")

    clone_scores    = [s for s, l in zip(y_scores, y_true) if l == 1]
    noclone_scores  = [s for s, l in zip(y_scores, y_true) if l == 0]
    print()
    print("-" * 60)
    print("SCORE DISTRIBUTIONS")
    print("-" * 60)
    print(f"  Clone pairs     — mean:{np.mean(clone_scores):.3f}  "
          f"min:{np.min(clone_scores):.3f}  max:{np.max(clone_scores):.3f}")
    print(f"  Non-clone pairs — mean:{np.mean(noclone_scores):.3f}  "
          f"min:{np.min(noclone_scores):.3f}  max:{np.max(noclone_scores):.3f}")
    print()


def _manual_metrics(y_true, y_pred):
    """Fallback if sklearn unavailable."""
    tp = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 1)
    fp = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 0)
    tn = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 0)
    acc = (tp + tn) / len(y_true)
    prec = tp / (tp + fp) if (tp + fp) else 0
    rec  = tp / (tp + fn) if (tp + fn) else 0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    print(f"TP:{tp}  FP:{fp}  FN:{fn}  TN:{tn}")
    print(f"Accuracy:{acc:.4f}  Precision:{prec:.4f}  Recall:{rec:.4f}  F1:{f1:.4f}")


def _print_samples(pairs, y_true, y_pred, y_scores, n=5):
    fp_cases = [
        (y_scores[i], pairs[i][0], pairs[i][1])
        for i in range(len(y_true))
        if y_true[i] == 0 and y_pred[i] == 1
    ]
    fn_cases = [
        (y_scores[i], pairs[i][0], pairs[i][1])
        for i in range(len(y_true))
        if y_true[i] == 1 and y_pred[i] == 0
    ]

    fp_cases.sort(reverse=True)
    fn_cases.sort()

    print("-" * 60)
    print(f"TOP FALSE POSITIVES (non-clone predicted as clone) — {len(fp_cases)} total")
    print("-" * 60)
    for score, fa, fb in fp_cases[:n]:
        print(f"  score={score:.3f}  {Path(fa).name}  vs  {Path(fb).name}")

    print()
    print("-" * 60)
    print(f"TOP FALSE NEGATIVES (clone missed) — {len(fn_cases)} total")
    print("-" * 60)
    for score, fa, fb in fn_cases[:n]:
        print(f"  score={score:.3f}  {Path(fa).name}  vs  {Path(fb).name}")
    print()


if __name__ == "__main__":
    run()
