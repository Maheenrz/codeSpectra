#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solves(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solves(sum_val - 1) + solves(sum_val - 2);
}
