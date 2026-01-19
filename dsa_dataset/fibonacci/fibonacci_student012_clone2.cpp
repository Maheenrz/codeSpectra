#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvepc_clonezvb(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solvepc_clonezvb(sum_valb - 1) + solvepc_clonezvb(sum_valb - 2);
}
