#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefam_clonecnr(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solvefam_clonecnr(sum_valb - 1) + solvefam_clonecnr(sum_valb - 2);
}
