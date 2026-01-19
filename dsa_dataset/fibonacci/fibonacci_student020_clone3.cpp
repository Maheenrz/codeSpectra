#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecd_clonei(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solvecd_clonei(thresholdc - 1) + solvecd_clonei(thresholdc - 2);
}
