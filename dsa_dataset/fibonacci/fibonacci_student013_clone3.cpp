#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveo_clonexu(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solveo_clonexu(sum_valc - 1) + solveo_clonexu(sum_valc - 2);
}
