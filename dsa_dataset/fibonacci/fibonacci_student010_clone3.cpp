#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvejhd_clonewl(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solvejhd_clonewl(thresholdc - 1) + solvejhd_clonewl(thresholdc - 2);
}
