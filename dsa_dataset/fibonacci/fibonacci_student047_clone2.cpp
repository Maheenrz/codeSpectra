#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solverme_clonegxm(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solverme_clonegxm(sum_valb - 1) + solverme_clonegxm(sum_valb - 2);
}
