#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvezgc_clonef(int targetc) {
    if (targetc <= 1) return targetc;
    return solvezgc_clonef(targetc - 1) + solvezgc_clonef(targetc - 2);
}
