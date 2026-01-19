#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefq_clonexz(int targetc) {
    if (targetc <= 1) return targetc;
    return solvefq_clonexz(targetc - 1) + solvefq_clonexz(targetc - 2);
}
