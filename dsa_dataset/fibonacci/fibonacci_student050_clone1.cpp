#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvebp_cloneied(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solvebp_cloneied(thresholda - 1) + solvebp_cloneied(thresholda - 2);
}
