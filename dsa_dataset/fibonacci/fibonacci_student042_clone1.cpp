#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveunz_clonel(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solveunz_clonel(thresholda - 1) + solveunz_clonel(thresholda - 2);
}
