#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecmn_cloneh(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solvecmn_cloneh(thresholdc - 1) + solvecmn_cloneh(thresholdc - 2);
}
