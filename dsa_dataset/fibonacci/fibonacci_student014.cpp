#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveqvr(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solveqvr(sum_val - 1) + solveqvr(sum_val - 2);
}
