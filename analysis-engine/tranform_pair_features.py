import sys
import csv
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent

# Make analysis-engine importable
sys.path.insert(0, str(THIS_DIR))

# IMPORTANT: use your actual adapter filename
from core.ast_ml_adapter import ASTMLAdapter

DSA_DATASET_PATH = REPO_ROOT / "dsa_dataset"
PAIRS_CSV = DSA_DATASET_PATH / "pairs.csv"
OUTPUT_CSV = DSA_DATASET_PATH / "pairs_features.csv"
CACHE_DIR = THIS_DIR / "feature_cache"

def build_unit_map(adapter: ASTMLAdapter):
    unit_map = {}
    cpp_files = list(DSA_DATASET_PATH.rglob("*.cpp"))
    for cpp in cpp_files:
        try:
            units = adapter.build_units_from_file(str(cpp))
        except Exception as e:
            print(f"[ERROR] {cpp}: {e}")
            continue
        for u in units:
            try:
                adapter.normalize_unit(u)
                adapter.compute_subtree_hashes(u)
                adapter.extract_ast_paths(u)
                adapter.compute_ast_counts(u)
                unit_map[u.id] = u
            except Exception as e:
                print(f"[WARN] Failed to finalize unit {u.id} ({cpp.name}): {e}")
    print(f"[INFO] Prepared {len(unit_map)} units.")
    return unit_map

def make_row(adapter: ASTMLAdapter, ua, ub, label: int):
    feats = adapter.make_pair_features(ua, ub)
    ta = ua.features.get("token_count", 0)
    tb = ub.features.get("token_count", 0)
    row = {
        "jaccard_subtrees": feats.get("jaccard_subtrees", 0.0),
        "cosine_paths": feats.get("cosine_paths", 0.0),
        "abs_token_count_diff": abs(ta - tb),
        "avg_token_count": 0.5 * (ta + tb),
        "subtree_count_A": len(ua.subtree_hashes or []),
        "subtree_count_B": len(ub.subtree_hashes or []),
        "path_count_A": len(ua.ast_paths or []),
        "path_count_B": len(ub.ast_paths or []),
        "token_count_A": ta,
        "token_count_B": tb,
        "call_approx_A": ua.features.get("call_approx", 0),
        "call_approx_B": ub.features.get("call_approx", 0),
        "label": int(label),
    }
    return row

def main():
    adapter = ASTMLAdapter(cache_dir=str(CACHE_DIR))
    unit_map = build_unit_map(adapter)
    if not PAIRS_CSV.exists():
        print(f"[ERROR] pairs.csv not found at {PAIRS_CSV}")
        return

    rows = []
    missing = 0
    with PAIRS_CSV.open("r") as f:
        reader = csv.reader(f)
        _ = next(reader, None)  # header
        for idx, row in enumerate(reader, start=1):
            if len(row) < 3:
                continue
            ua_id, ub_id, lbl = row
            ua = unit_map.get(ua_id)
            ub = unit_map.get(ub_id)
            if ua is None or ub is None:
                print(f"[WARN] Missing unit for pair #{idx}: {ua_id} or {ub_id}")
                missing += 1
                continue
            rows.append(make_row(adapter, ua, ub, int(lbl)))

    if not rows:
        print("[ERROR] No pair features produced.")
        return

    fieldnames = list(rows[0].keys())
    with OUTPUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[INFO] Wrote {len(rows)} rows to {OUTPUT_CSV} (missing pairs: {missing}).")

if __name__ == "__main__":
    main()