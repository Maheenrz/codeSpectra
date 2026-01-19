#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvepc(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solvepc(sum_val - 1) + solvepc(sum_val - 2);
}
