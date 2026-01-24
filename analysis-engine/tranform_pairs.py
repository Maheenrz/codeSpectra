import os
import sys
import csv
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent

# Ensure analysis-engine is importable
sys.path.insert(0, str(THIS_DIR))
from core.ast_ml_adapter import ASTMLAdapter  # use the adapter file you're actively using

DSA_DATASET_PATH = REPO_ROOT / "dsa_dataset"
OUTPUT_CSV = DSA_DATASET_PATH / "pairs_transformed.csv"
PAIRS_CSV = DSA_DATASET_PATH / "pairs.csv"
CACHE_DIR = THIS_DIR / "feature_cache"

def get_cpp_files(base_dir: Path) -> List[Path]:
    cpp_files = list(base_dir.rglob("*.cpp"))
    if not cpp_files:
        print(f"[ERROR] No .cpp files found in {base_dir}")
    return cpp_files

def preprocess_units(ast_adapter: ASTMLAdapter, cpp_files: List[Path]) -> Tuple[List, Dict[str, int]]:
    """
    Build and preprocess ALL units once (normalize -> hashes -> paths -> counts).
    Returns:
      - units_all: list of units in a stable order
      - id_to_index: map from unit.id to index in units_all
    """
    units_all = []
    id_to_index: Dict[str, int] = {}
    produced_ids = []

    for cpp_file in cpp_files:
        rel = cpp_file.relative_to(REPO_ROOT)
        print(f"[INFO] Parsing file: {rel}")
        try:
            units = ast_adapter.build_units_from_file(str(cpp_file))
            if not units:
                print(f"[WARNING] No units parsed for {cpp_file.name}")
                continue
            for unit in units:
                try:
                    ast_adapter.normalize_unit(unit)
                    ast_adapter.compute_subtree_hashes(unit)
                    ast_adapter.extract_ast_paths(unit)
                    ast_adapter.compute_ast_counts(unit)
                    id_to_index[unit.id] = len(units_all)
                    units_all.append(unit)
                    produced_ids.append(unit.id)
                except Exception as e:
                    print(f"[ERROR] Failed preprocessing unit {unit.id} in {cpp_file.name}: {e}")
        except Exception as e:
            print(f"[ERROR] Could not process file {cpp_file}: {e}")

    # Dump produced IDs for sanity
    ids_path = DSA_DATASET_PATH / "unit_ids.txt"
    try:
        with ids_path.open("w") as f:
            for uid in sorted(set(produced_ids)):
                f.write(uid + "\n")
        print(f"[INFO] Wrote produced unit IDs to {ids_path}")
    except Exception as e:
        print(f"[WARNING] Failed to write unit IDs file: {e}")

    print(f"[INFO] Prepared {len(units_all)} units from {len(cpp_files)} files.")
    return units_all, id_to_index

def vectorize_corpus(ast_adapter: ASTMLAdapter, units_all: List) -> np.ndarray:
    """
    Fit TF-IDF ONCE across all units (consistent dimensionality).
    Returns X of shape (n_units, d). Also sets unit.vector for each unit.
    """
    if not units_all:
        return np.zeros((0, 0), dtype=np.float32)
    X, ids = ast_adapter.vectorize_units(units_all, method="tfidf")
    print(f"[INFO] Vectorized corpus: {X.shape[0]} units, {X.shape[1]} features.")
    return X

def transform_pairs(pairs_csv: Path, id_to_index: Dict[str, int], X: np.ndarray, output_csv: Path):
    if not pairs_csv.exists():
        raise FileNotFoundError(f"[ERROR] pairs.csv not found at: {pairs_csv}")

    pairs = []
    with pairs_csv.open("r") as file:
        reader = csv.reader(file)
        header = next(reader, None)
        for row in reader:
            if len(row) >= 3:
                pairs.append(row)

    transformed_data = []
    missing = 0
    for idx, (unit_a_id, unit_b_id, label) in enumerate(pairs, start=1):
        ia = id_to_index.get(unit_a_id, None)
        ib = id_to_index.get(unit_b_id, None)
        if ia is None or ib is None:
            print(f"[WARNING] Missing vectors for pair #{idx}: {unit_a_id} or {unit_b_id}. Skipping...")
            missing += 1
            continue
        va = X[ia]
        vb = X[ib]
        transformed_data.append(list(va) + list(vb) + [int(label)])

    if not transformed_data:
        print("[ERROR] No pairs could be transformed. Check ID matching (filename.cpp:functionName).")
        return

    d = X.shape[1]
    header = [f"unitA_f{i}" for i in range(d)] + [f"unitB_f{i}" for i in range(d)] + ["label"]

    with output_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(transformed_data)

    print(f"[INFO] Transformed pairs saved to: {output_csv}")
    print(f"[INFO] Total pairs: {len(pairs)} | Written: {len(transformed_data)} | Skipped (missing): {missing}")

def main():
    ast_adapter = ASTMLAdapter(cache_dir=str(CACHE_DIR))
    cpp_files = get_cpp_files(DSA_DATASET_PATH)
    if not cpp_files:
        return
    units_all, id_to_index = preprocess_units(ast_adapter, cpp_files)
    if not units_all:
        print("[ERROR] No units prepared. Exiting...")
        return
    X = vectorize_corpus(ast_adapter, units_all)
    if X.size == 0:
        print("[ERROR] Vectorization failed. Exiting...")
        return
    transform_pairs(PAIRS_CSV, id_to_index, X, OUTPUT_CSV)

if __name__ == "__main__":
    main()