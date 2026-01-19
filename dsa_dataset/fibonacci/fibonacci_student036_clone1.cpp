#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvevk_clonebe(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solvevk_clonebe(thresholda - 1) + solvevk_clonebe(thresholda - 2);
}
