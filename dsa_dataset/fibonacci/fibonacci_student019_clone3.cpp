#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvewu_clonecwx(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solvewu_clonecwx(sum_valc - 1) + solvewu_clonecwx(sum_valc - 2);
}
