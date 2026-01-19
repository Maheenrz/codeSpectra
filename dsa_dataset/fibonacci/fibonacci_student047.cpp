#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solverme(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solverme(sum_val - 1) + solverme(sum_val - 2);
}
