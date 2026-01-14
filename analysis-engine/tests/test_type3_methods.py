import os
import sys

# Ensure the project root is in the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from detectors.type3.hybrid_detector import Type3HybridDetector

def run_test():
    # 1. Setup the Detector
    detector = Type3HybridDetector()
    
    # 2. Define paths to your test files 
    # (Adjust these paths based on your 'data/uploads' folder)
    base_path = "data/uploads/batch_1767113411"
    
    # Let's pick three files to represent a "Batch"
    test_files = [
        os.path.join(base_path, "Student_1_Original.cpp"),
        os.path.join(base_path, "Student_2_Renamed.cpp"),
        os.path.join(base_path, "Student_10_Matrix.cpp") # Likely different logic
    ]

    # Verify files exist before running
    for f in test_files:
        if not os.path.exists(f):
            print(f"❌ Error: File not found at {f}")
            return

    print("--- 🚀 Starting Type-3 Integration Test ---")
    
    # STEP 1: PREPARE BATCH (Training the Frequency Filter)
    print("\n[Step 1] Training Frequency Filter on batch...")
    detector.prepare_batch(test_files)
    print(f"Common hashes identified: {len(detector.freq_filter.common_hashes)}")

    # STEP 2: COMPARE CLONE (Original vs Renamed)
    print("\n[Step 2] Comparing Original vs Renamed (Should be HIGH score)...")
    result_clone = detector.detect(test_files[0], test_files[1])
    display_results(test_files[0], test_files[1], result_clone)

    # STEP 3: COMPARE DIFFERENT (Original vs Matrix)
    print("\n[Step 3] Comparing Original vs Different Logic (Should be LOW score)...")
    result_diff = detector.detect(test_files[0], test_files[2])
    display_results(test_files[0], test_files[2], result_diff)

def display_results(file_a, file_b, result):
    name_a = os.path.basename(file_a)
    name_b = os.path.basename(file_b)
    
    print(f"\n📊 Results for: {name_a} vs {name_b}")
    print(f"{'─' * 50}")
    print(f"🏆 Final Score: {result['score'] * 100:.2f}%")
    print(f"🚨 Is Clone:   {result['is_clone']}")
    print(f"\nBreakdown:")
    print(f"  - Winnowing Score: {result['details']['winnowing_fingerprint_score']:.4f}")
    print(f"  - AST Skeleton:    {result['details']['ast_skeleton_score']:.4f}")
    print(f"  - Complexity:      {result['details']['complexity_metric_score']:.4f}")
    print(f"{'─' * 50}\n")

if __name__ == "__main__":
    run_test()