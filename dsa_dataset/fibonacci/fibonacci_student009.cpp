#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveto(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solveto(sum_val - 1) + solveto(sum_val - 2);
}
