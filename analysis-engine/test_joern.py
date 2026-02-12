#!/usr/bin/env python3
"""
Test script for Joern Clone Detector
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from joern import JoernDetector

def main():
    print("=" * 60)
    print("JOERN CLONE DETECTOR TEST")
    print("=" * 60)
    
    # Test code 1 - Original factorial
    code1 = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''
    
    # Test code 2 - Renamed variables (Type-2 clone)
    code2 = '''
def compute_factorial(x):
    if x <= 1:
        return 1
    return x * compute_factorial(x - 1)
'''
    
    # Test code 3 - Different implementation (Type-4 clone)
    code3 = '''
def factorial_iterative(n):
    result = 1
    for i in range(1, n + 1):
        result = result * i
    return result
'''
    
    # Test code 4 - Completely different
    code4 = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
'''
    
    print("\n1. Checking Docker status...")
    detector = JoernDetector()
    status = detector.check_docker_status()
    print(f"   Docker available: {status['docker_available']}")
    print(f"   Container running: {status['running']}")
    
    if not status['docker_available']:
        print("\n❌ Docker is not available. Please start Docker Desktop.")
        return
    
    print("\n2. Testing: Original vs Renamed (Expected: Type-2 Clone)")
    print("-" * 40)
    result1 = detector.detect_clones(code1, code2)
    print(f"   Status: {result1.status}")
    print(f"   Is Clone: {result1.is_clone}")
    print(f"   Clone Type: {result1.clone_type.value}")
    print(f"   Similarity: {result1.scores.overall * 100:.1f}%")
    print(f"   Confidence: {result1.confidence.value}")
    
    print("\n3. Testing: Recursive vs Iterative (Expected: Type-4 Clone)")
    print("-" * 40)
    result2 = detector.detect_clones(code1, code3)
    print(f"   Status: {result2.status}")
    print(f"   Is Clone: {result2.is_clone}")
    print(f"   Clone Type: {result2.clone_type.value}")
    print(f"   Similarity: {result2.scores.overall * 100:.1f}%")
    print(f"   Confidence: {result2.confidence.value}")
    
    print("\n4. Testing: Factorial vs BubbleSort (Expected: NOT Clone)")
    print("-" * 40)
    result3 = detector.detect_clones(code1, code4)
    print(f"   Status: {result3.status}")
    print(f"   Is Clone: {result3.is_clone}")
    print(f"   Clone Type: {result3.clone_type.value}")
    print(f"   Similarity: {result3.scores.overall * 100:.1f}%")
    print(f"   Confidence: {result3.confidence.value}")
    
    print("\n5. Detailed Result for Test 1:")
    print("-" * 40)
    print(result1.get_summary())
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
