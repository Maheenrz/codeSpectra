#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvett_cloneut(int destb) {
    if (destb <= 1) return destb;
    return solvett_cloneut(destb - 1) + solvett_cloneut(destb - 2);
}
