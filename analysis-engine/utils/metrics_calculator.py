# analysis-engine/utils/metrics_calculator.py
import lizard
import numpy as np

class MetricsCalculator:
    def calculate_file_metrics(self, file_path):
        """
        Calculates Type-3 relevant metrics: LOC, Cyclomatic Complexity, Func Count.
        Returns a list [nloc, complexity, function_count]
        """
        try:
            path_str = str(file_path)
            # lizard handles C++, Java, Python, JS automatically
            analysis = lizard.analyze_file(path_str)
            
            total_nloc = analysis.nloc
            total_complexity = 0
            function_count = len(analysis.function_list)
            
            # Sum complexity of all functions
            for func in analysis.function_list:
                total_complexity += func.cyclomatic_complexity
            
            # If code has no functions (script style), use average complexity
            if function_count == 0 and total_nloc > 0:
                total_complexity = 1 

            return [total_nloc, total_complexity, function_count]
        except Exception as e:
            print(f"Error calculating metrics for {file_path}: {e}")
            return [0, 0, 0]

    def calculate_similarity(self, metrics_a, metrics_b):
        """
        Calculates similarity between two metric vectors using Euclidean distance.
        """
        vec_a = np.array(metrics_a)
        vec_b = np.array(metrics_b)
        
        # Euclidean distance
        dist = np.linalg.norm(vec_a - vec_b)
        
        # Normalize to 0-1 score (1 / 1+distance)
        # We add a small epsilon to avoid division by zero if needed, though +1 handles it
        return 1 / (1 + dist)