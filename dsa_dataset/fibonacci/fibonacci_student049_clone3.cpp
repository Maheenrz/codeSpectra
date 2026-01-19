#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvemdq_clonebry(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solvemdq_clonebry(sum_valc - 1) + solvemdq_clonebry(sum_valc - 2);
}
