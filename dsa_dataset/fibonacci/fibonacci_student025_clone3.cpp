#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedz_cloneimy(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solvedz_cloneimy(sum_valc - 1) + solvedz_cloneimy(sum_valc - 2);
}
