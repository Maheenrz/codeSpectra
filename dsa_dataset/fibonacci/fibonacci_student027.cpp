#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvedpn(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solvedpn(sum_val - 1) + solvedpn(sum_val - 2);
}
