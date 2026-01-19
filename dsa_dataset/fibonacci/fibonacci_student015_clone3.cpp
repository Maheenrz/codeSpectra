#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveioc_cloneg(int targetc) {
    if (targetc <= 1) return targetc;
    return solveioc_cloneg(targetc - 1) + solveioc_cloneg(targetc - 2);
}
