#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvehw_clonesd(int goalb) {
    if (goalb <= 1) return goalb;
    return solvehw_clonesd(goalb - 1) + solvehw_clonesd(goalb - 2);
}
