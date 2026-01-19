#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveqvr_cloneaz(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solveqvr_cloneaz(sum_valc - 1) + solveqvr_cloneaz(sum_valc - 2);
}
