#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvekvu_cloneish(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solvekvu_cloneish(thresholdb - 1) + solvekvu_cloneish(thresholdb - 2);
}
