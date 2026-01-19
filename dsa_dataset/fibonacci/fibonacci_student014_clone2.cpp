#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveqvr_clonekg(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solveqvr_clonekg(sum_valb - 1) + solveqvr_clonekg(sum_valb - 2);
}
