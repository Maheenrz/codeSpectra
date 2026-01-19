#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvepc_cloneyp(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solvepc_cloneyp(sum_valc - 1) + solvepc_cloneyp(sum_valc - 2);
}
