#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveiv(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solveiv(sum_val - 1) + solveiv(sum_val - 2);
}
