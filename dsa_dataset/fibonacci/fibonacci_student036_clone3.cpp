#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvevk_clonerl(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solvevk_clonerl(thresholdc - 1) + solvevk_clonerl(thresholdc - 2);
}
