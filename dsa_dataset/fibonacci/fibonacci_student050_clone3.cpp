#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvebp_cloneuy(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solvebp_cloneuy(thresholdc - 1) + solvebp_cloneuy(thresholdc - 2);
}
