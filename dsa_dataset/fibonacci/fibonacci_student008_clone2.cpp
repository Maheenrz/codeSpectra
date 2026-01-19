#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveuij_clonexw(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solveuij_clonexw(thresholdb - 1) + solveuij_clonexw(thresholdb - 2);
}
