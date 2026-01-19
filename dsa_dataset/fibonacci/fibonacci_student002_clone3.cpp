#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvej_clonekp(int targetc) {
    if (targetc <= 1) return targetc;
    return solvej_clonekp(targetc - 1) + solvej_clonekp(targetc - 2);
}
