#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedal_clonelbf(int destc) {
    if (destc <= 1) return destc;
    return solvedal_clonelbf(destc - 1) + solvedal_clonelbf(destc - 2);
}
