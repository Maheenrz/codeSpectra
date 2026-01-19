#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvevk_clonev(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solvevk_clonev(thresholdb - 1) + solvevk_clonev(thresholdb - 2);
}
