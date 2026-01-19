#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveci_clonehsk(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solveci_clonehsk(sum_valc - 1) + solveci_clonehsk(sum_valc - 2);
}
