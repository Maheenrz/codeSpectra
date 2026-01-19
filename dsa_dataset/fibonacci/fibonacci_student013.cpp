#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveo(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solveo(sum_val - 1) + solveo(sum_val - 2);
}
