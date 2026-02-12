#!/usr/bin/env python3
"""
Type-4 Semantic Clone Detection Test - All Languages

Tests the Joern-based detector for Type-4 (semantic) clones across:
- Python
- Java
- JavaScript
- C
- C++

This tests the JoernDetector which uses Program Dependence Graph (PDG)
analysis to find code that performs the same functionality but is
implemented differently.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our JoernDetector
from joern_detector import JoernDetector


def main():
    print("=" * 70)
    print("JOERN TYPE-4 SEMANTIC CLONE DETECTOR - MULTI-LANGUAGE TEST")
    print("=" * 70)
    
    # Create detector
    detector = JoernDetector()
    
    # Check status
    status = detector.get_status()
    print(f"\n📋 Detector Status:")
    print(f"   Docker Available: {status['docker_available']}")
    print(f"   Container Running: {status['container_running']}")
    print(f"   Supported Languages: {', '.join(status['supported_languages'])}")
    print(f"   Default Threshold: {status['default_threshold'] * 100:.0f}%")
    
    # Define test cases for each language
    tests = [
        # ═══════════════════════════════════════════════════════════════
        # PYTHON TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "Python: Recursive vs Iterative Factorial",
            "language": "python",
            "expected": True,  # These ARE semantic clones (same behavior)
            "code1": '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
''',
            "code2": '''
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result = result * i
    return result
'''
        },
        {
            "name": "Python: List Sum - Loop vs Builtin",
            "language": "python",
            "expected": True,  # Same behavior, different implementation
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
            "name": "Python: NOT Clone - Sort vs Search",
            "language": "python",
            "expected": False,  # Different functionality entirely
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
            "name": "Java: Array vs ArrayList Stack",
            "language": "java",
            "expected": True,  # Same Stack behavior, different data structure
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
            "name": "Java: Recursive vs Iterative Fibonacci",
            "language": "java",
            "expected": True,  # Same Fibonacci behavior
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
        
        # ═══════════════════════════════════════════════════════════════
        # JAVASCRIPT TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "JavaScript: Callback vs Promise",
            "language": "javascript",
            "expected": True,  # Same async data fetching behavior
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
            "name": "JavaScript: For Loop vs Reduce",
            "language": "javascript",
            "expected": True,  # Same sum behavior
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
        
        # ═══════════════════════════════════════════════════════════════
        # C TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "C: Recursive vs Iterative GCD",
            "language": "c",
            "expected": True,  # Same GCD algorithm behavior
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
            "name": "C: Array Index vs Pointer Traversal",
            "language": "c",
            "expected": True,  # Same sum behavior, different traversal
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
        
        # ═══════════════════════════════════════════════════════════════
        # C++ TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "C++: Array vs Vector Stack",
            "language": "cpp",
            "expected": True,  # Same Stack behavior
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
            "name": "C++: NOT Clone - Stack vs Queue",
            "language": "cpp",
            "expected": False,  # Different data structure behavior (LIFO vs FIFO)
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
    
    # Run tests
    print("\n" + "=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}: {test['name']}")
        print(f"Language: {test['language'].upper()}")
        print(f"Expected: {'SEMANTIC CLONE' if test['expected'] else 'NOT CLONE'}")
        print(f"{'─' * 70}")
        
        # Call our JoernDetector
        result = detector.detect(
            test['code1'],
            test['code2'],
            test['language']
        )
        
        if result.status == "error":
            print(f"  ❌ ERROR: {result.error_message}")
            results.append((test['name'], test['language'], "ERROR", test['expected'], False))
        else:
            # Check if prediction matches expected
            correct = result.is_semantic_clone == test['expected']
            icon = "✅" if correct else "❌"
            
            print(f"  {icon} Is Semantic Clone: {result.is_semantic_clone}")
            print(f"  📈 Similarity: {result.similarity * 100:.1f}%")
            print(f"  🎯 Confidence: {result.confidence.value}")
            print(f"  ⏱️  Time: {result.analysis_time_ms:.1f}ms")
            print(f"  ")
            print(f"  Detailed Scores:")
            print(f"    Node Types:    {result.scores.node_type_similarity * 100:.1f}%")
            print(f"    Control Flow:  {result.scores.control_flow_similarity * 100:.1f}%")
            print(f"    Data Flow:     {result.scores.data_flow_similarity * 100:.1f}%")
            print(f"    Structure:     {result.scores.structural_similarity * 100:.1f}%")
            
            results.append((
                test['name'], 
                test['language'], 
                result.is_semantic_clone, 
                test['expected'],
                correct
            ))
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    # Group by language
    languages = {}
    for name, lang, got, expected, correct in results:
        if lang not in languages:
            languages[lang] = {"correct": 0, "total": 0}
        languages[lang]["total"] += 1
        if correct:
            languages[lang]["correct"] += 1
    
    print(f"\n{'Language':<15} {'Correct':<10} {'Total':<10} {'Accuracy':<10}")
    print("-" * 45)
    
    total_correct = 0
    total_tests = 0
    
    for lang, stats in languages.items():
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{lang.upper():<15} {stats['correct']:<10} {stats['total']:<10} {acc:.1f}%")
        total_correct += stats['correct']
        total_tests += stats['total']
    
    print("-" * 45)
    overall_acc = (total_correct / total_tests * 100) if total_tests > 0 else 0
    print(f"{'OVERALL':<15} {total_correct:<10} {total_tests:<10} {overall_acc:.1f}%")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)
    
    # Final verdict
    print(f"\n🎯 Type-4 Semantic Clone Detection Accuracy: {overall_acc:.1f}%")
    
    if overall_acc >= 80:
        print("✅ EXCELLENT - JoernDetector is working well!")
    elif overall_acc >= 60:
        print("⚠️ GOOD - JoernDetector is working with some limitations")
    else:
        print("❌ NEEDS IMPROVEMENT - Consider adjusting thresholds")


if __name__ == "__main__":
    main()#!/usr/bin/env python3
"""
Type-4 Semantic Clone Detection Test - All Languages

Tests the Joern-based detector across:
- Python
- Java
- JavaScript
- C
- C++
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from semantic_clone_detector import SemanticCloneDetector


def main():
    print("=" * 70)
    print("TYPE-4 SEMANTIC CLONE DETECTOR - MULTI-LANGUAGE TEST")
    print("=" * 70)
    
    detector = SemanticCloneDetector()
    
    # Check status
    status = detector.check_status()
    print(f"\n📋 Detector Status:")
    print(f"   Docker Available: {status['docker_available']}")
    print(f"   Container Running: {status['container_running']}")
    print(f"   Supported Languages: {', '.join(status['supported_languages'])}")
    print(f"   Default Threshold: {status['default_threshold'] * 100:.0f}%")
    
    # Define test cases for each language
    tests = [
        # ═══════════════════════════════════════════════════════════════
        # PYTHON TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "Python: Recursive vs Iterative Factorial",
            "language": "python",
            "expected": True,
            "code1": '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
''',
            "code2": '''
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result = result * i
    return result
'''
        },
        {
            "name": "Python: List Sum - Loop vs Builtin",
            "language": "python",
            "expected": True,
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
            "name": "Python: NOT Clone - Sort vs Search",
            "language": "python",
            "expected": False,
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
            "name": "Java: Array vs ArrayList Implementation",
            "language": "java",
            "expected": True,
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
            "name": "Java: Recursive vs Iterative Fibonacci",
            "language": "java",
            "expected": True,
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
        
        # ═══════════════════════════════════════════════════════════════
        # JAVASCRIPT TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "JavaScript: Callback vs Promise Pattern",
            "language": "javascript",
            "expected": True,
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
            "name": "JavaScript: For Loop vs Map/Reduce",
            "language": "javascript",
            "expected": True,
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
        
        # ═══════════════════════════════════════════════════════════════
        # C TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "C: Recursive vs Iterative GCD",
            "language": "c",
            "expected": True,
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
            "name": "C: Array vs Pointer Traversal",
            "language": "c",
            "expected": True,
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
        
        # ═══════════════════════════════════════════════════════════════
        # C++ TESTS
        # ═══════════════════════════════════════════════════════════════
        {
            "name": "C++: Vector vs Array Implementation",
            "language": "cpp",
            "expected": True,
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
            "name": "C++: NOT Clone - Stack vs Queue",
            "language": "cpp",
            "expected": False,
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
    
    # Run tests
    print("\n" + "=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}: {test['name']}")
        print(f"Language: {test['language'].upper()}")
        print(f"Expected: {'SEMANTIC CLONE' if test['expected'] else 'NOT CLONE'}")
        print(f"{'─' * 70}")
        
        result = detector.detect(
            test['code1'],
            test['code2'],
            test['language']
        )
        
        if result.status == "error":
            print(f"  ❌ ERROR: {result.error_message}")
            results.append((test['name'], test['language'], "ERROR", test['expected'], False))
        else:
            # Check if prediction matches expected
            correct = result.is_semantic_clone == test['expected']
            icon = "✅" if correct else "❌"
            
            print(f"  {icon} Is Semantic Clone: {result.is_semantic_clone}")
            print(f"  📈 Similarity: {result.similarity * 100:.1f}%")
            print(f"  🎯 Confidence: {result.confidence.value}")
            print(f"  ⏱️  Time: {result.analysis_time_ms:.1f}ms")
            print(f"  ")
            print(f"  Scores:")
            print(f"    Node Types:    {result.scores.node_type_similarity * 100:.1f}%")
            print(f"    Control Flow:  {result.scores.control_flow_similarity * 100:.1f}%")
            print(f"    Data Flow:     {result.scores.data_flow_similarity * 100:.1f}%")
            print(f"    Structure:     {result.scores.structural_similarity * 100:.1f}%")
            
            results.append((
                test['name'], 
                test['language'], 
                result.is_semantic_clone, 
                test['expected'],
                correct
            ))
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    # Group by language
    languages = {}
    for name, lang, got, expected, correct in results:
        if lang not in languages:
            languages[lang] = {"correct": 0, "total": 0}
        languages[lang]["total"] += 1
        if correct:
            languages[lang]["correct"] += 1
    
    print(f"\n{'Language':<15} {'Correct':<10} {'Total':<10} {'Accuracy':<10}")
    print("-" * 45)
    
    total_correct = 0
    total_tests = 0
    
    for lang, stats in languages.items():
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{lang.upper():<15} {stats['correct']:<10} {stats['total']:<10} {acc:.1f}%")
        total_correct += stats['correct']
        total_tests += stats['total']
    
    print("-" * 45)
    overall_acc = (total_correct / total_tests * 100) if total_tests > 0 else 0
    print(f"{'OVERALL':<15} {total_correct:<10} {total_tests:<10} {overall_acc:.1f}%")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)
    
    # Final verdict
    print(f"\n🎯 Type-4 Semantic Clone Detection Accuracy: {overall_acc:.1f}%")
    
    if overall_acc >= 80:
        print("✅ EXCELLENT - Detector is working well!")
    elif overall_acc >= 60:
        print("⚠️ GOOD - Detector is working with some limitations")
    else:
        print("❌ NEEDS IMPROVEMENT - Consider adjusting thresholds")


if __name__ == "__main__":
    main()
