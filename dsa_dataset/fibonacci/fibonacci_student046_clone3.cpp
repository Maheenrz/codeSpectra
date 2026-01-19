#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefam_cloneoyu(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solvefam_cloneoyu(sum_valc - 1) + solvefam_cloneoyu(sum_valc - 2);
}
