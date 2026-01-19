#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveunz_clonevpr(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solveunz_clonevpr(thresholdb - 1) + solveunz_clonevpr(thresholdb - 2);
}
