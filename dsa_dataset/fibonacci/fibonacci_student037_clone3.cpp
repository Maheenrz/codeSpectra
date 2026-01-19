#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveiv_clonen(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solveiv_clonen(sum_valc - 1) + solveiv_clonen(sum_valc - 2);
}
