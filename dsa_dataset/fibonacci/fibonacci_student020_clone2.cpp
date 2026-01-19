#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecd_clonezpk(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solvecd_clonezpk(thresholdb - 1) + solvecd_clonezpk(thresholdb - 2);
}
