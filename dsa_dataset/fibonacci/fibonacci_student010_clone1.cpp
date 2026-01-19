#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvejhd_clonejx(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solvejhd_clonejx(thresholda - 1) + solvejhd_clonejx(thresholda - 2);
}
