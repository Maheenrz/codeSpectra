#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvejhd_cloneq(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solvejhd_cloneq(thresholdb - 1) + solvejhd_cloneq(thresholdb - 2);
}
