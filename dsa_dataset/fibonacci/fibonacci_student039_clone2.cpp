#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvelmu_cloneik(int destb) {
    if (destb <= 1) return destb;
    return solvelmu_cloneik(destb - 1) + solvelmu_cloneik(destb - 2);
}
