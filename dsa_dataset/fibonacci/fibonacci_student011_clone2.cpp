#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecww_clonewvx(int destb) {
    if (destb <= 1) return destb;
    return solvecww_clonewvx(destb - 1) + solvecww_clonewvx(destb - 2);
}
