#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveiv_cloneqhg(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solveiv_cloneqhg(sum_valb - 1) + solveiv_cloneqhg(sum_valb - 2);
}
