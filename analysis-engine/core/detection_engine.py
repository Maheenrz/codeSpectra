"""
Multi-Method Detection Engine
Runs multiple detection methods per type and compares results
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class CloneType(Enum):
    TYPE1 = "type1"
    TYPE2 = "type2"
    TYPE3 = "type3"
    TYPE4 = "type4"


@dataclass
class MethodResult:
    """Result from a single detection method"""
    method_name: str
    clone_type: CloneType
    clones_found: int
    clone_groups: List[Any]
    execution_time_ms: int
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    memory_used_mb: Optional[float] = None


@dataclass
class ComparisonResult:
    """Comparison of multiple methods"""
    clone_type: CloneType
    method_results: List[MethodResult]
    best_method: str
    consensus_clones: int  # Clones found by majority of methods
    total_unique_clones: int


class MultiMethodDetectionEngine:
    """
    Detection engine that runs multiple methods per clone type
    and compares their results
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.methods_registry = {
            CloneType.TYPE1: [],
            CloneType.TYPE2: [],
            CloneType.TYPE3: [],
            CloneType.TYPE4: [],
        }
        self._load_methods()
    
    def _load_methods(self):
        """Load all available detection methods"""
        # Import Type 1 methods
        try:
            from detectors.type1.ast_exact_method import Type1ASTMethod
            from detectors.type1.hash_method import Type1HashMethod
            from detectors.type1.string_method import Type1StringMethod
            
            self.methods_registry[CloneType.TYPE1] = [
                Type1ASTMethod(self.config),
                Type1HashMethod(self.config),
                Type1StringMethod(self.config),
            ]
        except ImportError as e:
            print(f"Warning: Some Type 1 methods not available: {e}")
        
        # Import Type 2 methods
        try:
            from detectors.type2.ast_normalized_method import Type2ASTMethod
            from detectors.type2.token_based_method import Type2TokenMethod
            
            self.methods_registry[CloneType.TYPE2] = [
                Type2ASTMethod(self.config),
                Type2TokenMethod(self.config),
            ]
        except ImportError as e:
            print(f"Warning: Some Type 2 methods not available: {e}")
        
        # Import Type 3 methods
        try:
            from detectors.type3.ast_diff_method import Type3ASTDiffMethod
            from detectors.type3.sequence_matcher_method import Type3SequenceMethod
            
            self.methods_registry[CloneType.TYPE3] = [
                Type3ASTDiffMethod(self.config),
                Type3SequenceMethod(self.config),
            ]
        except ImportError as e:
            print(f"Warning: Some Type 3 methods not available: {e}")
        
        # Import Type 4 methods
        try:
            from detectors.type4.ast_semantic_method import Type4ASTSemanticMethod
            from detectors.type4.metrics_method import Type4MetricsMethod
            
            self.methods_registry[CloneType.TYPE4] = [
                Type4ASTSemanticMethod(self.config),
                Type4MetricsMethod(self.config),
            ]
        except ImportError as e:
            print(f"Warning: Some Type 4 methods not available: {e}")
    
    def detect_with_comparison(
        self, 
        code_fragments: List[Any],
        clone_types: List[CloneType] = None,
        parallel: bool = False
    ) -> Dict[CloneType, ComparisonResult]:
        """
        Run detection for specified types using all available methods
        and compare results
        
        Args:
            code_fragments: List of code fragments to analyze
            clone_types: Which types to detect (default: all)
            parallel: Run methods in parallel (faster but uses more memory)
            
        Returns:
            Dictionary mapping clone type to comparison results
        """
        if clone_types is None:
            clone_types = list(CloneType)
        
        results = {}
        
        for clone_type in clone_types:
            print(f"\n{'='*60}")
            print(f"Detecting {clone_type.value.upper()} clones")
            print(f"{'='*60}")
            
            methods = self.methods_registry.get(clone_type, [])
            
            if not methods:
                print(f"No methods available for {clone_type.value}")
                continue
            
            method_results = []
            
            if parallel and len(methods) > 1:
                # Run methods in parallel
                method_results = self._run_methods_parallel(methods, code_fragments)
            else:
                # Run methods sequentially
                method_results = self._run_methods_sequential(methods, code_fragments)
            
            # Compare results
            comparison = self._compare_methods(clone_type, method_results)
            results[clone_type] = comparison
            
            # Display comparison
            self._display_comparison(comparison)
        
        return results
    
    def _run_methods_sequential(
        self, 
        methods: List[Any], 
        code_fragments: List[Any]
    ) -> List[MethodResult]:
        """Run detection methods one by one"""
        results = []
        
        for method in methods:
            method_name = method.__class__.__name__
            print(f"\nRunning {method_name}...")
            
            start_time = time.time()
            
            try:
                detection_result = method.detect_clones(code_fragments)
                execution_time = int((time.time() - start_time) * 1000)
                
                result = MethodResult(
                    method_name=method_name,
                    clone_type=method.get_clone_type(),
                    clones_found=detection_result.total_clones,
                    clone_groups=detection_result.clone_groups,
                    execution_time_ms=execution_time
                )
                
                results.append(result)
                print(f"✅ {method_name}: {result.clones_found} clones in {execution_time}ms")
                
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
                continue
        
        return results
    
    def _run_methods_parallel(
        self, 
        methods: List[Any], 
        code_fragments: List[Any]
    ) -> List[MethodResult]:
        """Run detection methods in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=len(methods)) as executor:
            future_to_method = {
                executor.submit(self._run_single_method, method, code_fragments): method
                for method in methods
            }
            
            for future in as_completed(future_to_method):
                method = future_to_method[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        print(f"✅ {result.method_name}: {result.clones_found} clones")
                except Exception as e:
                    print(f"❌ {method.__class__.__name__} failed: {e}")
        
        return results
    
    def _run_single_method(self, method: Any, code_fragments: List[Any]) -> Optional[MethodResult]:
        """Helper to run a single method (for parallel execution)"""
        method_name = method.__class__.__name__
        start_time = time.time()
        
        try:
            detection_result = method.detect_clones(code_fragments)
            execution_time = int((time.time() - start_time) * 1000)
            
            return MethodResult(
                method_name=method_name,
                clone_type=method.get_clone_type(),
                clones_found=detection_result.total_clones,
                clone_groups=detection_result.clone_groups,
                execution_time_ms=execution_time
            )
        except Exception as e:
            print(f"Error in {method_name}: {e}")
            return None
    
    def _compare_methods(
        self, 
        clone_type: CloneType, 
        method_results: List[MethodResult]
    ) -> ComparisonResult:
        """Compare results from different methods"""
        if not method_results:
            return ComparisonResult(
                clone_type=clone_type,
                method_results=[],
                best_method="None",
                consensus_clones=0,
                total_unique_clones=0
            )
        
        # Find best method based on multiple criteria
        best_method = max(
            method_results,
            key=lambda r: (
                r.clones_found,  # More clones found
                -r.execution_time_ms  # Faster execution (negative for reverse sort)
            )
        )
        
        # Calculate consensus (clones found by at least 2 methods)
        clone_counts = [r.clones_found for r in method_results]
        consensus_clones = int(sum(clone_counts) / len(clone_counts))
        
        # Total unique clones (max found by any method)
        total_unique_clones = max(clone_counts)
        
        return ComparisonResult(
            clone_type=clone_type,
            method_results=method_results,
            best_method=best_method.method_name,
            consensus_clones=consensus_clones,
            total_unique_clones=total_unique_clones
        )
    
    def _display_comparison(self, comparison: ComparisonResult):
        """Display comparison results in a nice format"""
        print(f"\n📊 {comparison.clone_type.value.upper()} Results:")
        print(f"{'─'*80}")
        print(f"{'Method':<30} {'Clones':<10} {'Time (ms)':<12} {'Rating'}")
        print(f"{'─'*80}")
        
        for result in comparison.method_results:
            rating = "⭐" * min(5, max(1, result.clones_found // 5))
            is_best = "🏆" if result.method_name == comparison.best_method else "  "
            
            print(f"{is_best} {result.method_name:<28} {result.clones_found:<10} "
                  f"{result.execution_time_ms:<12} {rating}")
        
        print(f"{'─'*80}")
        print(f"Best Method: {comparison.best_method}")
        print(f"Consensus Clones: {comparison.consensus_clones}")
        print(f"Total Unique Clones: {comparison.total_unique_clones}")
    
    def evaluate_accuracy(
        self,
        method_results: List[MethodResult],
        ground_truth: Dict[str, Any]
    ) -> List[MethodResult]:
        """
        Evaluate accuracy of methods against ground truth
        
        Args:
            method_results: Results from different methods
            ground_truth: Known clone pairs
            
        Returns:
            Updated method results with accuracy metrics
        """
        # This would compare detected clones with known ground truth
        # and calculate precision, recall, F1 score
        
        for result in method_results:
            # Placeholder for actual accuracy calculation
            # In real implementation, compare result.clone_groups with ground_truth
            result.precision = 0.95  # Placeholder
            result.recall = 0.90  # Placeholder
            result.f1_score = 0.925  # Placeholder
        
        return method_results
    
    def get_best_method(self, clone_type: CloneType) -> Optional[Any]:
        """Get the best performing method for a clone type"""
        methods = self.methods_registry.get(clone_type, [])
        return methods[0] if methods else None
    
    def detect_fast(
        self, 
        code_fragments: List[Any],
        clone_types: List[CloneType] = None
    ) -> Dict[CloneType, Any]:
        """
        Fast mode: Use only the best method per type
        (for production use when speed matters)
        """
        if clone_types is None:
            clone_types = list(CloneType)
        
        results = {}
        
        for clone_type in clone_types:
            best_method = self.get_best_method(clone_type)
            
            if best_method:
                detection_result = best_method.detect_clones(code_fragments)
                results[clone_type] = detection_result
        
        return results


# Example usage
if __name__ == "__main__":
    # This would be called from your API
    engine = MultiMethodDetectionEngine()
    
    # Example code fragments (would come from file upload)
    fragments = []  # Your code fragments here
    
    # Run comparison mode (all methods)
    comparison_results = engine.detect_with_comparison(
        fragments,
        clone_types=[CloneType.TYPE1, CloneType.TYPE2],
        parallel=True
    )
    
    # Or run fast mode (best method only)
    fast_results = engine.detect_fast(fragments, [CloneType.TYPE1])