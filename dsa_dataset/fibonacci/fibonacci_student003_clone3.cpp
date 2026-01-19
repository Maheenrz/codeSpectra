#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvekvu_clonel(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solvekvu_clonel(thresholdc - 1) + solvekvu_clonel(thresholdc - 2);
}
