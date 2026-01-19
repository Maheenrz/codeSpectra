#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvedz(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solvedz(sum_val - 1) + solvedz(sum_val - 2);
}
