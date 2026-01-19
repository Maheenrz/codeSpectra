#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveuij_clonekpi(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solveuij_clonekpi(thresholda - 1) + solveuij_clonekpi(thresholda - 2);
}
