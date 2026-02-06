# analysis-engine/training/extract_features.py

"""
Extract features from code pairs using AST ML Adapter.
This is the SAME process used for real submissions!
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import numpy as np
import pandas as pd
from tqdm import tqdm

# Add parent to path for imports
TRAINING_DIR = Path(__file__).resolve().parent
ENGINE_DIR = TRAINING_DIR.parent
sys.path.insert(0, str(ENGINE_DIR))

from core.ast_ml_adapter import ASTMLAdapter


class FeatureExtractor:
    """
    Extract features from code pairs.
    SAME adapter used for real student submissions!
    """
    
    def __init__(self):
        self.adapter = ASTMLAdapter(cache_dir=str(ENGINE_DIR / "feature_cache"))
        
        # Define feature names (must match what hybrid_detector expects!)
        self.feature_names = [
            "jaccard_subtrees",
            "cosine_paths",
            "abs_token_count_diff",
            "avg_token_count",
            "subtree_count_A",
            "subtree_count_B",
            "path_count_A",
            "path_count_B",
            "token_count_A",
            "token_count_B",
            "call_approx_A",
            "call_approx_B",
        ]
    
    def extract_pair_features(
        self,
        code_a: str,
        code_b: str,
        language: str,
        pair_id: str
    ) -> Optional[Dict[str, float]]:
        """
        Extract features for a single pair of code snippets.
        THIS IS EXACTLY WHAT HAPPENS WITH REAL SUBMISSIONS!
        
        Args:
            code_a: First code snippet
            code_b: Second code snippet  
            language: Programming language
            pair_id: Identifier for this pair
        
        Returns:
            Dictionary of features or None if extraction fails
        """
        
        # Step 1: Parse code into Units
        unit_a = self.adapter.build_unit_from_code_string(
            code_a, language, f"{pair_id}_A"
        )
        unit_b = self.adapter.build_unit_from_code_string(
            code_b, language, f"{pair_id}_B"
        )
        
        if unit_a is None or unit_b is None:
            return None
        
        try:
            # Step 2: Normalize (removes language-specific identifiers)
            self.adapter.normalize_unit(unit_a)
            self.adapter.normalize_unit(unit_b)
            
            # Step 3: Compute subtree hashes
            self.adapter.compute_subtree_hashes(unit_a)
            self.adapter.compute_subtree_hashes(unit_b)
            
            # Step 4: Extract AST paths
            self.adapter.extract_ast_paths(unit_a)
            self.adapter.extract_ast_paths(unit_b)
            
            # Step 5: Compute AST counts
            self.adapter.compute_ast_counts(unit_a)
            self.adapter.compute_ast_counts(unit_b)
            
            # Step 6: Make pair features
            pair_feats = self.adapter.make_pair_features(unit_a, unit_b)
            
            # Step 7: Add individual unit features
            fa = unit_a.features or {}
            fb = unit_b.features or {}
            
            features = {
                "jaccard_subtrees": pair_feats.get("jaccard_subtrees", 0.0),
                "cosine_paths": pair_feats.get("cosine_paths", 0.0),
                "abs_token_count_diff": pair_feats.get("abs_token_count_diff", 0.0),
                "avg_token_count": pair_feats.get("avg_token_count", 0.0),
                "subtree_count_A": len(unit_a.subtree_hashes or set()),
                "subtree_count_B": len(unit_b.subtree_hashes or set()),
                "path_count_A": len(unit_a.ast_paths or []),
                "path_count_B": len(unit_b.ast_paths or []),
                "token_count_A": fa.get("token_count", 0),
                "token_count_B": fb.get("token_count", 0),
                "call_approx_A": fa.get("call_approx", 0),
                "call_approx_B": fb.get("call_approx", 0),
            }
            
            return features
            
        except Exception as e:
            print(f"⚠️ Feature extraction failed for {pair_id}: {e}")
            return None
    
    def extract_all_features(
        self,
        pairs_df: pd.DataFrame,
        output_path: str = None
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Extract features for all pairs in the dataset.
        
        Args:
            pairs_df: DataFrame with columns [code_a, code_b, label, language]
            output_path: Path to save features CSV
        
        Returns:
            X (features array), y (labels array), feature_names
        """
        
        if output_path is None:
            output_path = str(ENGINE_DIR / "data" / "features" / "features.csv")
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        print("=" * 60)
        print("🔄 Extracting Features from Code Pairs")
        print("=" * 60)
        print(f"   Total pairs: {len(pairs_df)}")
        print(f"   Languages: {pairs_df['language'].unique().tolist()}")
        print(f"   Output: {output_path}")
        print()
        
        all_features = []
        all_labels = []
        failed_count = 0
        
        # Process with progress bar
        for idx, row in tqdm(pairs_df.iterrows(), total=len(pairs_df), desc="Extracting"):
            features = self.extract_pair_features(
                code_a=row['code_a'],
                code_b=row['code_b'],
                language=row['language'],
                pair_id=f"pair_{idx}"
            )
            
            if features is not None:
                # Convert to vector in consistent order
                feature_vector = [features[name] for name in self.feature_names]
                all_features.append(feature_vector)
                all_labels.append(row['label'])
            else:
                failed_count += 1
        
        print(f"\n✅ Extraction Complete:")
        print(f"   Successful: {len(all_features)} pairs")
        print(f"   Failed: {failed_count} pairs")
        print(f"   Success rate: {100*len(all_features)/(len(all_features)+failed_count):.1f}%")
        
        # Convert to arrays
        X = np.array(all_features, dtype=np.float32)
        y = np.array(all_labels, dtype=np.int32)
        
        # Save to CSV
        output_df = pd.DataFrame(X, columns=self.feature_names)
        output_df['label'] = y
        output_df.to_csv(output_path, index=False)
        print(f"\n💾 Saved features to: {output_path}")
        
        # Also save feature names for model loading
        import json
        names_path = Path(output_path).parent / "feature_names.json"
        with open(names_path, 'w') as f:
            json.dump(self.feature_names, f, indent=2)
        print(f"💾 Saved feature names to: {names_path}")
        
        return X, y, self.feature_names


def main():
    """Main function to extract features from downloaded dataset"""
    
    # Load combined dataset
    data_path = ENGINE_DIR / "data" / "combined_dataset.parquet"
    
    if not data_path.exists():
        print("❌ Dataset not found. Run download_datasets.py first!")
        print(f"   Expected: {data_path}")
        sys.exit(1)
    
    print(f"📂 Loading dataset from: {data_path}")
    pairs_df = pd.read_parquet(data_path)
    print(f"   Loaded {len(pairs_df)} pairs")
    
    # Extract features
    extractor = FeatureExtractor()
    X, y, feature_names = extractor.extract_all_features(pairs_df)
    
    print(f"\n📊 Final Feature Matrix:")
    print(f"   Shape: {X.shape}")
    print(f"   Features: {feature_names}")
    print(f"   Labels: {np.bincount(y)}")


if __name__ == "__main__":
    main()