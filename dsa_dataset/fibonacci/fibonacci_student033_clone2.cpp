#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvemv_clonez(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solvemv_clonez(thresholdb - 1) + solvemv_clonez(thresholdb - 2);
}
