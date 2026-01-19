#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvett_clonegic(int destc) {
    if (destc <= 1) return destc;
    return solvett_clonegic(destc - 1) + solvett_clonegic(destc - 2);
}
