#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvemdq(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solvemdq(sum_val - 1) + solvemdq(sum_val - 2);
}
