#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solverme_clonecf(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solverme_clonecf(sum_valc - 1) + solverme_clonecf(sum_valc - 2);
}
