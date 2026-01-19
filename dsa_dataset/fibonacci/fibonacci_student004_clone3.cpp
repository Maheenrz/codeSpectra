#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvea_cloneiio(int destc) {
    if (destc <= 1) return destc;
    return solvea_cloneiio(destc - 1) + solvea_cloneiio(destc - 2);
}
