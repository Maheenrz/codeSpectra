#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecmn_clonedmk(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solvecmn_clonedmk(thresholdb - 1) + solvecmn_clonedmk(thresholdb - 2);
}
