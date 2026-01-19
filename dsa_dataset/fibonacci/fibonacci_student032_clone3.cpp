#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvej_clonexj(int targetc) {
    if (targetc <= 1) return targetc;
    return solvej_clonexj(targetc - 1) + solvej_clonexj(targetc - 2);
}
