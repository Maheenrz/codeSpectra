#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveuij_clonegs(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solveuij_clonegs(thresholdc - 1) + solveuij_clonegs(thresholdc - 2);
}
