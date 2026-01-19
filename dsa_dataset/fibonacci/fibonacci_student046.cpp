#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvefam(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solvefam(sum_val - 1) + solvefam(sum_val - 2);
}
