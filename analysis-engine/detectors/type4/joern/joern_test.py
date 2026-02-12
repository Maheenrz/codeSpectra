# detectors/type4/joern/tests/joern_test.py

#!/usr/bin/env python3
"""
Type-4 Semantic Clone Detection Test - Multi-Language Suite

Tests the Joern-based Type-4 detector across multiple languages:
- Python
- Java  
- JavaScript
- C
- C++

This validates the JoernDetector which uses Program Dependence Graph (PDG)
analysis to detect code that performs the same functionality but is
implemented differently (Type-4 semantic clones).

Usage:
    python joern_test.py
    python joern_test.py --verbose
    python joern_test.py --language python
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from joern_detector import JoernDetector
except ImportError as e:
    print(f"❌ Error importing JoernDetector: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_header(text, char='='):
    """Print a formatted header"""
    width = 70
    print(f"\n{Colors.BOLD}{char * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{text.center(width)}{Colors.RESET}")
    print(f"{Colors.BOLD}{char * width}{Colors.RESET}")


def print_test_header(test_num, test_name, language, expected):
    """Print test case header"""
    print(f"\n{Colors.CYAN}{'─' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST {test_num}: {test_name}{Colors.RESET}")
    print(f"Language: {Colors.MAGENTA}{language.upper()}{Colors.RESET}")
    expected_str = "SEMANTIC CLONE" if expected else "NOT CLONE"
    color = Colors.GREEN if expected else Colors.YELLOW
    print(f"Expected: {color}{expected_str}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")


def get_test_cases():
    """Define all test cases"""
    return [
        # ═══════════════════════════════════════════════════════════════
        # PYTHON TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "Recursive vs Iterative Factorial",
            "language": "python",
            "expected": True,
            "description": "Same factorial computation, different approach (recursion vs loop)",
            "code1": '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
''',
            "code2": '''
def factorial_iterative(num):
    result = 1
    for i in range(1, num + 1):
        result = result * i
    return result
'''
        },
        {
            "name": "List Sum - Loop vs Builtin",
            "language": "python",
            "expected": True,
            "description": "Same sum operation, manual loop vs built-in function",
            "code1": '''
def sum_list(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
''',
            "code2": '''
def sum_list(numbers):
    return sum(numbers)
'''
        },
        {
            "name": "Fibonacci - Recursive vs Dynamic Programming",
            "language": "python",
            "expected": True,
            "description": "Same Fibonacci sequence, recursive vs DP approach",
            "code1": '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
''',
            "code2": '''
def fibonacci_dp(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
'''
        },
        {
            "name": "NOT Clone - Sort vs Search",
            "language": "python",
            "expected": False,
            "description": "Different functionality - sorting vs searching (should NOT be clone)",
            "code1": '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
''',
            "code2": '''
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
'''
        },
        
        # ═══════════════════════════════════════════════════════════════
        # JAVA TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "Array vs ArrayList Stack Implementation",
            "language": "java",
            "expected": True,
            "description": "Same Stack behavior, different underlying data structure",
            "code1": '''
public class ArrayStack {
    private int[] data;
    private int top;
    
    public ArrayStack(int size) {
        data = new int[size];
        top = -1;
    }
    
    public void push(int value) {
        data[++top] = value;
    }
    
    public int pop() {
        return data[top--];
    }
    
    public boolean isEmpty() {
        return top == -1;
    }
}
''',
            "code2": '''
import java.util.ArrayList;

public class ListStack {
    private ArrayList<Integer> data;
    
    public ListStack() {
        data = new ArrayList<>();
    }
    
    public void push(int value) {
        data.add(value);
    }
    
    public int pop() {
        return data.remove(data.size() - 1);
    }
    
    public boolean isEmpty() {
        return data.isEmpty();
    }
}
'''
        },
        {
            "name": "Recursive vs Iterative Fibonacci",
            "language": "java",
            "expected": True,
            "description": "Same Fibonacci computation, different implementation",
            "code1": '''
public class Fibonacci {
    public int calculate(int n) {
        if (n <= 1) return n;
        return calculate(n-1) + calculate(n-2);
    }
}
''',
            "code2": '''
public class Fibonacci {
    public int calculate(int n) {
        if (n <= 1) return n;
        int a = 0, b = 1;
        for (int i = 2; i <= n; i++) {
            int temp = a + b;
            a = b;
            b = temp;
        }
        return b;
    }
}
'''
        },
        {
            "name": "Traditional Loop vs Stream API",
            "language": "java",
            "expected": True,
            "description": "Same filtering operation, imperative vs functional style",
            "code1": '''
public List<Integer> filterEven(List<Integer> numbers) {
    List<Integer> result = new ArrayList<>();
    for (Integer num : numbers) {
        if (num % 2 == 0) {
            result.add(num);
        }
    }
    return result;
}
''',
            "code2": '''
public List<Integer> filterEven(List<Integer> numbers) {
    return numbers.stream()
                  .filter(n -> n % 2 == 0)
                  .collect(Collectors.toList());
}
'''
        },
        
        # ═══════════════════════════════════════════════════════════════
        # JAVASCRIPT TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "Callback vs Promise Pattern",
            "language": "javascript",
            "expected": True,
            "description": "Same async data fetching, callback vs Promise approach",
            "code1": '''
function fetchData(callback) {
    setTimeout(function() {
        const data = { id: 1, name: "test" };
        callback(null, data);
    }, 1000);
}

function processData(data) {
    return data.name.toUpperCase();
}
''',
            "code2": '''
function fetchData() {
    return new Promise((resolve) => {
        setTimeout(() => {
            const data = { id: 1, name: "test" };
            resolve(data);
        }, 1000);
    });
}

function processData(data) {
    return data.name.toUpperCase();
}
'''
        },
        {
            "name": "For Loop vs Reduce",
            "language": "javascript",
            "expected": True,
            "description": "Same array sum, imperative loop vs functional reduce",
            "code1": '''
function sumArray(arr) {
    let total = 0;
    for (let i = 0; i < arr.length; i++) {
        total += arr[i];
    }
    return total;
}
''',
            "code2": '''
function sumArray(arr) {
    return arr.reduce((acc, val) => acc + val, 0);
}
'''
        },
        {
            "name": "Traditional vs Arrow Function",
            "language": "javascript",
            "expected": True,
            "description": "Same map operation, different function syntax",
            "code1": '''
function doubleValues(arr) {
    return arr.map(function(x) {
        return x * 2;
    });
}
''',
            "code2": '''
const doubleValues = (arr) => {
    return arr.map(x => x * 2);
};
'''
        },
        
        # ═══════════════════════════════════════════════════════════════
        # C TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "Recursive vs Iterative GCD",
            "language": "c",
            "expected": True,
            "description": "Same GCD algorithm, recursive vs iterative",
            "code1": '''
int gcd(int a, int b) {
    if (b == 0)
        return a;
    return gcd(b, a % b);
}
''',
            "code2": '''
int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}
'''
        },
        {
            "name": "Array Index vs Pointer Arithmetic",
            "language": "c",
            "expected": True,
            "description": "Same array sum, index access vs pointer traversal",
            "code1": '''
int sum_array(int arr[], int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += arr[i];
    }
    return total;
}
''',
            "code2": '''
int sum_array(int* arr, int n) {
    int total = 0;
    int* end = arr + n;
    while (arr < end) {
        total += *arr;
        arr++;
    }
    return total;
}
'''
        },
        {
            "name": "String Copy - strcpy vs Manual",
            "language": "c",
            "expected": True,
            "description": "Same string copy operation, library vs manual",
            "code1": '''
void copy_string(char* dest, const char* src) {
    strcpy(dest, src);
}
''',
            "code2": '''
void copy_string(char* dest, const char* src) {
    while (*src != '\\0') {
        *dest = *src;
        dest++;
        src++;
    }
    *dest = '\\0';
}
'''
        },
        
        # ═══════════════════════════════════════════════════════════════
        # C++ TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "Array vs Vector Stack",
            "language": "cpp",
            "expected": True,
            "description": "Same Stack ADT, raw array vs std::vector",
            "code1": '''
class Stack {
private:
    int* data;
    int top;
    int capacity;
public:
    Stack(int cap) : capacity(cap), top(-1) {
        data = new int[capacity];
    }
    
    void push(int val) {
        data[++top] = val;
    }
    
    int pop() {
        return data[top--];
    }
    
    bool empty() {
        return top == -1;
    }
    
    ~Stack() {
        delete[] data;
    }
};
''',
            "code2": '''
#include <vector>

class Stack {
private:
    std::vector<int> data;
public:
    void push(int val) {
        data.push_back(val);
    }
    
    int pop() {
        int val = data.back();
        data.pop_back();
        return val;
    }
    
    bool empty() {
        return data.empty();
    }
};
'''
        },
        {
            "name": "Bubble Sort vs Selection Sort",
            "language": "cpp",
            "expected": True,
            "description": "Same sorting result, different algorithms",
            "code1": '''
void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n-1; i++) {
        for (int j = 0; j < n-i-1; j++) {
            if (arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
}
''',
            "code2": '''
void selectionSort(int arr[], int n) {
    for (int i = 0; i < n-1; i++) {
        int min_idx = i;
        for (int j = i+1; j < n; j++) {
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        swap(arr[i], arr[min_idx]);
    }
}
'''
        },
        {
            "name": "NOT Clone - Stack vs Queue",
            "language": "cpp",
            "expected": False,
            "description": "Different data structure semantics - LIFO vs FIFO (should NOT be clone)",
            "code1": '''
class Stack {
    int data[100];
    int top = -1;
public:
    void push(int x) { data[++top] = x; }
    int pop() { return data[top--]; }
};
''',
            "code2": '''
class Queue {
    int data[100];
    int front = 0, rear = 0;
public:
    void enqueue(int x) { data[rear++] = x; }
    int dequeue() { return data[front++]; }
};
'''
        },
    ]


def run_tests(detector, tests, verbose=False, language_filter=None):
    """Run all test cases"""
    print_header("RUNNING TYPE-4 SEMANTIC CLONE DETECTION TESTS")
    
    results = []
    total_time = 0
    
    for i, test in enumerate(tests, 1):
        # Skip if language filter is set and doesn't match
        if language_filter and test['language'] != language_filter:
            continue
        
        print_test_header(i, test['name'], test['language'], test['expected'])
        
        if verbose:
            print(f"\n{Colors.BLUE}Description:{Colors.RESET} {test['description']}")
        
        # Run detection
        start_time = time.time()
        
        try:
            result = detector.detect(
                test['code1'],
                test['code2'],
                test['language']
            )
            
            elapsed = (time.time() - start_time) * 1000
            total_time += elapsed
            
            if result.status == "error":
                print(f"\n  {Colors.RED}❌ ERROR:{Colors.RESET} {result.error_message}")
                results.append({
                    'name': test['name'],
                    'language': test['language'],
                    'status': 'ERROR',
                    'expected': test['expected'],
                    'got': None,
                    'correct': False,
                    'time': elapsed
                })
            else:
                # Check correctness
                correct = result.is_semantic_clone == test['expected']
                icon = f"{Colors.GREEN}✅{Colors.RESET}" if correct else f"{Colors.RED}❌{Colors.RESET}"
                
                # Print results
                clone_str = f"{Colors.GREEN}YES{Colors.RESET}" if result.is_semantic_clone else f"{Colors.YELLOW}NO{Colors.RESET}"
                print(f"\n  {icon} Is Semantic Clone: {clone_str}")
                print(f"  📈 Overall Similarity: {Colors.BOLD}{result.similarity * 100:.1f}%{Colors.RESET}")
                print(f"  🎯 Confidence: {Colors.BOLD}{result.confidence.value}{Colors.RESET}")
                print(f"  ⏱️  Analysis Time: {elapsed:.1f}ms")
                
                # Detailed scores
                print(f"\n  {Colors.CYAN}Detailed Similarity Scores:{Colors.RESET}")
                print(f"    • Node Types:    {result.scores.node_type_similarity * 100:>5.1f}%")
                print(f"    • Control Flow:  {result.scores.control_flow_similarity * 100:>5.1f}%")
                print(f"    • Data Flow:     {result.scores.data_flow_similarity * 100:>5.1f}%")
                print(f"    • Structure:     {result.scores.structural_similarity * 100:>5.1f}%")
                
                # Threshold info
                threshold_pct = result.threshold_used * 100
                print(f"\n  📊 Threshold Used: {threshold_pct:.1f}%")
                
                # Verdict
                if correct:
                    print(f"  {Colors.GREEN}✓ CORRECT PREDICTION{Colors.RESET}")
                else:
                    expected_str = "clone" if test['expected'] else "non-clone"
                    got_str = "clone" if result.is_semantic_clone else "non-clone"
                    print(f"  {Colors.RED}✗ INCORRECT - Expected {expected_str}, got {got_str}{Colors.RESET}")
                
                # Verbose output
                if verbose and hasattr(result, 'pdg1_info') and hasattr(result, 'pdg2_info'):
                    print(f"\n  {Colors.BLUE}PDG Information:{Colors.RESET}")
                    print(f"    Code 1: {result.pdg1_info.num_nodes} nodes, {result.pdg1_info.num_edges} edges")
                    print(f"    Code 2: {result.pdg2_info.num_nodes} nodes, {result.pdg2_info.num_edges} edges")
                
                results.append({
                    'name': test['name'],
                    'language': test['language'],
                    'status': 'SUCCESS',
                    'expected': test['expected'],
                    'got': result.is_semantic_clone,
                    'similarity': result.similarity,
                    'confidence': result.confidence.value,
                    'correct': correct,
                    'time': elapsed
                })
                
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            print(f"\n  {Colors.RED}❌ EXCEPTION:{Colors.RESET} {str(e)}")
            if verbose:
                import traceback
                traceback.print_exc()
            
            results.append({
                'name': test['name'],
                'language': test['language'],
                'status': 'EXCEPTION',
                'expected': test['expected'],
                'got': None,
                'correct': False,
                'time': elapsed
            })
    
    return results, total_time


def print_summary(results, total_time):
    """Print test results summary"""
    print_header("RESULTS SUMMARY")
    
    # Overall stats
    total_tests = len(results)
    successful = [r for r in results if r['status'] == 'SUCCESS']
    correct = [r for r in results if r['correct']]
    errors = [r for r in results if r['status'] in ['ERROR', 'EXCEPTION']]
    
    # By language
    languages = {}
    for r in results:
        lang = r['language']
        if lang not in languages:
            languages[lang] = {'correct': 0, 'total': 0}
        languages[lang]['total'] += 1
        if r['correct']:
            languages[lang]['correct'] += 1
    
    # Print language breakdown
    print(f"\n{Colors.BOLD}Results by Language:{Colors.RESET}")
    print(f"\n{'Language':<15} {'Correct':<10} {'Total':<10} {'Accuracy':<10}")
    print("-" * 45)
    
    total_correct = 0
    total_count = 0
    
    for lang in sorted(languages.keys()):
        stats = languages[lang]
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        color = Colors.GREEN if acc >= 80 else Colors.YELLOW if acc >= 60 else Colors.RED
        print(f"{lang.upper():<15} {stats['correct']:<10} {stats['total']:<10} {color}{acc:.1f}%{Colors.RESET}")
        total_correct += stats['correct']
        total_count += stats['total']
    
    print("-" * 45)
    overall_acc = (total_correct / total_count * 100) if total_count > 0 else 0
    color = Colors.GREEN if overall_acc >= 80 else Colors.YELLOW if overall_acc >= 60 else Colors.RED
    print(f"{Colors.BOLD}{'OVERALL':<15} {total_correct:<10} {total_count:<10} {color}{overall_acc:.1f}%{Colors.RESET}")
    
    # Performance stats
    print(f"\n{Colors.BOLD}Performance:{Colors.RESET}")
    print(f"  Total Time: {total_time:.1f}ms")
    print(f"  Average Time per Test: {total_time / total_tests:.1f}ms")
    
    if successful:
        avg_similarity = sum(r['similarity'] for r in successful) / len(successful)
        print(f"  Average Similarity (all tests): {avg_similarity * 100:.1f}%")
    
    # Errors
    if errors:
        print(f"\n{Colors.RED}{Colors.BOLD}Errors/Exceptions: {len(errors)}{Colors.RESET}")
        for r in errors:
            print(f"  • {r['name']} ({r['language']}): {r['status']}")
    
    # Final verdict
    print_header("FINAL VERDICT")
    
    print(f"\n{Colors.BOLD}Type-4 Semantic Clone Detection Accuracy: {color}{overall_acc:.1f}%{Colors.RESET}\n")
    
    if overall_acc >= 80:
        print(f"{Colors.GREEN}✅ EXCELLENT{Colors.RESET} - JoernDetector is working very well!")
        print("   The detector successfully identifies semantic clones across languages.")
    elif overall_acc >= 60:
        print(f"{Colors.YELLOW}⚠️  GOOD{Colors.RESET} - JoernDetector is working with some limitations")
        print("   Consider reviewing failed cases and adjusting thresholds.")
    else:
        print(f"{Colors.RED}❌ NEEDS IMPROVEMENT{Colors.RESET} - Detector requires adjustment")
        print("   Review the configuration, thresholds, and feature weights.")
    
    print()


def main():
    """Main test execution"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Test Joern Type-4 Clone Detector')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--language', '-l', type=str, help='Filter by language (python, java, javascript, c, cpp)')
    args = parser.parse_args()
    
    # Print banner
    print_header("JOERN TYPE-4 SEMANTIC CLONE DETECTOR", '█')
    print(f"\n{Colors.BOLD}Multi-Language Test Suite{Colors.RESET}")
    print("Testing semantic clone detection across Python, Java, JavaScript, C, and C++")
    
    # Initialize detector
    print(f"\n{Colors.CYAN}Initializing detector...{Colors.RESET}")
    try:
        detector = JoernDetector(auto_start=True)
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to initialize detector: {e}{Colors.RESET}")
        print("\nMake sure:")
        print("  1. Docker is running")
        print("  2. Joern container is built (see docker/README.md)")
        print("  3. All dependencies are installed")
        return 1
    
    # Check status
    status = detector.get_status()
    print(f"\n{Colors.BOLD}📋 Detector Status:{Colors.RESET}")
    print(f"   Docker Available: {Colors.GREEN if status['docker_available'] else Colors.RED}{status['docker_available']}{Colors.RESET}")
    print(f"   Container Running: {Colors.GREEN if status['container_running'] else Colors.RED}{status['container_running']}{Colors.RESET}")
    print(f"   Supported Languages: {', '.join(status['supported_languages'])}")
    print(f"   Default Threshold: {status['default_threshold'] * 100:.0f}%")
    
    if not status['docker_available']:
        print(f"\n{Colors.RED}❌ Docker is not available!{Colors.RESET}")
        print("Please start Docker and try again.")
        return 1
    
    if not status['container_running']:
        print(f"\n{Colors.YELLOW}⚠️  Joern container is not running. Starting...{Colors.RESET}")
        if not detector.start_container():
            print(f"{Colors.RED}❌ Failed to start container!{Colors.RESET}")
            return 1
        print(f"{Colors.GREEN}✓ Container started{Colors.RESET}")
    
    # Get test cases
    tests = get_test_cases()
    
    # Filter by language if specified
    if args.language:
        original_count = len(tests)
        tests = [t for t in tests if t['language'] == args.language.lower()]
        print(f"\n{Colors.YELLOW}Filtering: {len(tests)} {args.language.upper()} tests (from {original_count} total){Colors.RESET}")
        
        if not tests:
            print(f"{Colors.RED}No tests found for language: {args.language}{Colors.RESET}")
            return 1
    
    # Run tests
    results, total_time = run_tests(detector, tests, verbose=args.verbose, language_filter=args.language)
    
    # Print summary
    print_summary(results, total_time)
    
    # Return exit code
    accuracy = (sum(1 for r in results if r['correct']) / len(results) * 100) if results else 0
    return 0 if accuracy >= 60 else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Test interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)