#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveglt_clonew(int destb) {
    if (destb <= 1) return destb;
    return solveglt_clonew(destb - 1) + solveglt_clonew(destb - 2);
}
