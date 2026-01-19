#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvemdq_cloneqnr(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solvemdq_cloneqnr(sum_valb - 1) + solvemdq_cloneqnr(sum_valb - 2);
}
