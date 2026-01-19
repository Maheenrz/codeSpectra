#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveci(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solveci(sum_val - 1) + solveci(sum_val - 2);
}
