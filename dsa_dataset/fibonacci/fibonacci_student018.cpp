#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveiy(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solveiy(sum_val - 1) + solveiy(sum_val - 2);
}
