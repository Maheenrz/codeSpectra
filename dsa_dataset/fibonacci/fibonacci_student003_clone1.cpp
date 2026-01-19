#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvekvu_clonec(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solvekvu_clonec(thresholda - 1) + solvekvu_clonec(thresholda - 2);
}
