#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveiy_clonec(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solveiy_clonec(sum_valc - 1) + solveiy_clonec(sum_valc - 2);
}
