from core.tokenizer import CodeTokenizer
from utils.metrics_calculator import MetricsCalculator
from core.ast_processor import ASTProcessor  
from detectors.type3.winnowing import WinnowingDetector
from utils.frequency_filter import BatchFrequencyFilter
from typing import List

class Type3HybridDetector:
    def __init__(self):
        self.tokenizer = CodeTokenizer()
        self.metrics_calc = MetricsCalculator()
        self.ast_processor = ASTProcessor()
        self.winnowing = WinnowingDetector(k=5, window_size=4)
        self.freq_filter = BatchFrequencyFilter(threshold=0.7)

    def prepare_batch(self, all_file_paths: List[str]):
        """
        Layer 1: Analyze the whole batch to find 'Common Code' (Boilerplate).
        This must be called before detect() to populate the frequency filter.
        """
        all_tokens = [self.tokenizer.tokenize_file(p) for p in all_file_paths]
        self.freq_filter.train_on_batch(all_tokens)

    def detect(self, file_path_a: str, file_path_b: str):
        """
        Core logic to compare two specific files using 3 layers of analysis.
        """
        # 1. Generate Tokens
        tokens_a = self.tokenizer.tokenize_file(file_path_a)
        tokens_b = self.tokenizer.tokenize_file(file_path_b)
        
        if not tokens_a or not tokens_b:
            return {'score': 0, 'is_clone': False, 'details': {}}

        # 2. Winnowing (DNA Fingerprinting) with Frequency Filtering
        set_a = self.winnowing.get_fingerprint(tokens_a)
        set_b = self.winnowing.get_fingerprint(tokens_b)
        
        # Remove Common 'Chaff' (Noise) identified in prepare_batch
        # This is what solves the "80% baseline similarity" problem
        set_a = {h for h in set_a if h not in self.freq_filter.common_hashes}
        set_b = {h for h in set_b if h not in self.freq_filter.common_hashes}
        
        winnowing_score = self.winnowing.calculate_similarity(set_a, set_b)

        # 3. AST (Structural Skeleton)
        # Matches the flow (loops, ifs) regardless of text
        ast_score = self.ast_processor.calculate_similarity(file_path_a, file_path_b)

        # 4. Metrics (Complexity Shape)
        metrics_a = self.metrics_calc.calculate_file_metrics(file_path_a)
        metrics_b = self.metrics_calc.calculate_file_metrics(file_path_b)
        metric_score = self.metrics_calc.calculate_similarity(metrics_a, metrics_b)

        # FINAL WEIGHTED DECISION
        # Winnowing: 50% | AST: 40% | Metrics: 10%
        final_score = (winnowing_score * 0.5) + (ast_score * 0.4) + (metric_score * 0.1)
        
        return {
            'score': round(float(final_score), 4),
            'is_clone': bool(final_score >= 0.65), 
            'details': {
                'winnowing_fingerprint_score': round(float(winnowing_score), 4),
                'ast_skeleton_score': round(float(ast_score), 4),
                'complexity_metric_score': round(float(metric_score), 4)
            }
        }

    def detect_clones(self, all_file_paths: List[str]):
        """
        Manager Method: Implements the All-Pairs Comparison logic.
        This is what the MultiMethodDetectionEngine calls to process a whole folder.
        """
        results = []
        n = len(all_file_paths)

        # Step A: Train the noise filter on all files first
        self.prepare_batch(all_file_paths)

        # Step B: All-Pairs Comparison Loop (i vs j)
        # Ensures 1 is compared with 2, 1 with 3, and 2 with 3.
        for i in range(n):
            for j in range(i + 1, n):
                file_a = all_file_paths[i]
                file_b = all_file_paths[j]

                comparison = self.detect(file_a, file_b)

                if comparison['is_clone']:
                    results.append({
                        'file_a': file_a,
                        'file_b': file_b,
                        'score': comparison['score'],
                        'details': comparison['details']
                    })

        # Wrap in the object expected by the Engine
        return DetectionResultWrapper(results)

    def get_clone_type(self):
        return "type3"


class DetectionResultWrapper:
    """
    Helper class to wrap results so they are compatible with the 
    MultiMethodDetectionEngine's MethodResult dataclass.
    """
    def __init__(self, matches):
        self.clone_groups = matches
        self.total_clones = len(matches)