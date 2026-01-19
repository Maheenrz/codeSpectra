#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvewu(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solvewu(sum_val - 1) + solvewu(sum_val - 2);
}
