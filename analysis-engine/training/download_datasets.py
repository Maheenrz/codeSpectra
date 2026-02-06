# analysis-engine/training/download_datasets.py

"""
Download and prepare datasets for training.
- BigCloneBench (Java) from HuggingFace
- Existing dsa_dataset (C++)
"""

import os
import sys
from pathlib import Path
from typing import Optional
import pandas as pd

# Add parent to path for imports
TRAINING_DIR = Path(__file__).resolve().parent
ENGINE_DIR = TRAINING_DIR.parent
sys.path.insert(0, str(ENGINE_DIR))


class DatasetDownloader:
    """Download and prepare training datasets"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = ENGINE_DIR / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.data_dir / "bigclonebench"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def download_bigclonebench(self, max_samples: Optional[int] = 100000) -> pd.DataFrame:
        """
        Download BigCloneBench from HuggingFace
        
        Args:
            max_samples: Maximum number of pairs to download (None for all)
                        Default 100K is enough for good training
        
        Returns:
            DataFrame with columns: [code_a, code_b, label, language]
        """
        print("=" * 60)
        print("📥 Downloading BigCloneBench from HuggingFace...")
        print("=" * 60)
        
        try:
            from datasets import load_dataset
        except ImportError:
            print("❌ Please install datasets: pip install datasets")
            sys.exit(1)
        
        # Check if already cached
        cache_file = self.cache_dir / "bigclonebench_processed.parquet"
        if cache_file.exists():
            print(f"✅ Found cached dataset at {cache_file}")
            df = pd.read_parquet(cache_file)
            print(f"   Loaded {len(df)} pairs from cache")
            return df
        
        # Download from HuggingFace
        print("⏳ Downloading... (this may take a few minutes)")
        ds = load_dataset("google/code_x_glue_cc_clone_detection_big_clone_bench")
        
        # Process all splits
        pairs = []
        for split in ['train', 'validation', 'test']:
            print(f"   Processing {split} split...")
            split_data = ds[split]
            
            for item in split_data:
                pairs.append({
                    'code_a': item['func1'],
                    'code_b': item['func2'],
                    'label': int(item['label']),
                    'language': 'java',
                    'source': 'bigclonebench',
                    'split': split
                })
        
        df = pd.DataFrame(pairs)
        
        print(f"\n📊 BigCloneBench Statistics:")
        print(f"   Total pairs: {len(df)}")
        print(f"   Clone pairs (label=1): {(df['label']==1).sum()}")
        print(f"   Non-clone pairs (label=0): {(df['label']==0).sum()}")
        
        # Sample if requested
        if max_samples and len(df) > max_samples:
            print(f"\n📉 Sampling {max_samples} pairs (balanced)...")
            
            # Stratified sampling to maintain label balance
            clones = df[df['label'] == 1].sample(n=max_samples//2, random_state=42)
            non_clones = df[df['label'] == 0].sample(n=max_samples//2, random_state=42)
            df = pd.concat([clones, non_clones]).sample(frac=1, random_state=42).reset_index(drop=True)
            
            print(f"   Sampled: {len(df)} pairs")
            print(f"   Clones: {(df['label']==1).sum()}, Non-clones: {(df['label']==0).sum()}")
        
        # Save to cache
        df.to_parquet(cache_file)
        print(f"\n💾 Saved to cache: {cache_file}")
        
        return df
    
    def load_dsa_dataset(self) -> pd.DataFrame:
        """
        Load your existing dsa_dataset (C++)
        
        Returns:
            DataFrame with columns: [code_a, code_b, label, language]
        """
        print("\n" + "=" * 60)
        print("📂 Loading existing dsa_dataset (C++)...")
        print("=" * 60)
        
        # Find dsa_dataset (could be in repo root or analysis-engine)
        possible_paths = [
            ENGINE_DIR.parent / "dsa_dataset",
            ENGINE_DIR / "dsa_dataset",
        ]
        
        dsa_path = None
        for p in possible_paths:
            if p.exists() and (p / "pairs.csv").exists():
                dsa_path = p
                break
        
        if dsa_path is None:
            print("⚠️ dsa_dataset not found. Skipping C++ data.")
            return pd.DataFrame()
        
        print(f"   Found at: {dsa_path}")
        
        # Load pairs.csv
        pairs_csv = dsa_path / "pairs.csv"
        pairs_df = pd.read_csv(pairs_csv)
        
        print(f"   Found {len(pairs_df)} pairs in pairs.csv")
        
        # Load actual code content
        pairs = []
        for _, row in pairs_df.iterrows():
            unit_a_id = row['unitA_id']  # e.g., "two_sum_student001.cpp:solvexyz"
            unit_b_id = row['unitB_id']
            label = row['label']
            
            code_a = self._load_code_from_unit_id(unit_a_id, dsa_path)
            code_b = self._load_code_from_unit_id(unit_b_id, dsa_path)
            
            if code_a and code_b:
                pairs.append({
                    'code_a': code_a,
                    'code_b': code_b,
                    'label': int(label),
                    'language': 'cpp',
                    'source': 'dsa_dataset',
                    'split': 'train'
                })
        
        df = pd.DataFrame(pairs)
        
        if len(df) > 0:
            print(f"\n📊 dsa_dataset Statistics:")
            print(f"   Loaded pairs: {len(df)}")
            print(f"   Clone pairs: {(df['label']==1).sum()}")
            print(f"   Non-clone pairs: {(df['label']==0).sum()}")
        
        return df
    
    def _load_code_from_unit_id(self, unit_id: str, base_path: Path) -> Optional[str]:
        """Extract code from unit ID like 'two_sum_student001.cpp:solvexyz'"""
        try:
            filename = unit_id.split(':')[0]  # "two_sum_student001.cpp"
            problem = filename.split('_student')[0]  # "two_sum"
            
            file_path = base_path / problem / filename
            if file_path.exists():
                return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            pass
        return None
    
    def create_combined_dataset(self, bcb_samples: int = 100000) -> pd.DataFrame:
        """
        Create dataset - PURE APPROACH 3 (Java only)
        """
        print("\n" + "=" * 60)
        print("🔄 Creating Dataset (Approach 3: Java Only)")
        print("=" * 60)
        
        # ONLY BigCloneBench (Java)
        combined = self.download_bigclonebench(max_samples=bcb_samples)
        
        # NO C++ data - pure transfer learning approach
        # dsa_df = self.load_dsa_dataset()  # COMMENTED OUT
        
        print(f"\n📊 Dataset Statistics:")
        print(f"   Total pairs: {len(combined)}")
        print(f"   Language: Java (100%)")
        print(f"   Clones: {(combined['label']==1).sum()}")
        print(f"   Non-clones: {(combined['label']==0).sum()}")
        
        # Save
        output_path = self.data_dir / "combined_dataset.parquet"
        combined.to_parquet(output_path)
        print(f"\n💾 Saved to: {output_path}")
        
        return combined

def main():
    """Main function to download and prepare datasets"""
    downloader = DatasetDownloader()
    
    # Create combined dataset
    # Use 100K samples from BigCloneBench (enough for good training)
    combined = downloader.create_combined_dataset(bcb_samples=100000)
    
    print("\n✅ Dataset preparation complete!")
    print(f"   Total pairs ready for feature extraction: {len(combined)}")


if __name__ == "__main__":
    main()