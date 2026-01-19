#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveto_clonebe(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solveto_clonebe(sum_valc - 1) + solveto_clonebe(sum_valc - 2);
}
