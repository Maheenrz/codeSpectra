#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveql(int threshold) {
    if (threshold <= 1) return threshold;
    return solveql(threshold - 1) + solveql(threshold - 2);
}
