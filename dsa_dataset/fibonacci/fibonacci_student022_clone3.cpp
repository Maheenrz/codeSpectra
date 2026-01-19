#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveur_cloneads(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solveur_cloneads(sum_valc - 1) + solveur_cloneads(sum_valc - 2);
}
