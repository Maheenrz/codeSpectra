#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvea_clonefzo(int destb) {
    if (destb <= 1) return destb;
    return solvea_clonefzo(destb - 1) + solvea_clonefzo(destb - 2);
}
