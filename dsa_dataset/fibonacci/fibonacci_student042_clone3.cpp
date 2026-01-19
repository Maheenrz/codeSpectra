#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveunz_cloneif(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solveunz_cloneif(thresholdc - 1) + solveunz_cloneif(thresholdc - 2);
}
