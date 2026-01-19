#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvebp_cloneyrz(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solvebp_cloneyrz(thresholdb - 1) + solvebp_cloneyrz(thresholdb - 2);
}
