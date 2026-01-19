#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecd_clonek(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solvecd_clonek(thresholda - 1) + solvecd_clonek(thresholda - 2);
}
