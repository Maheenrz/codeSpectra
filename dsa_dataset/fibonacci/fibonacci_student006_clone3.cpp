#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvehw_cloneil(int goalc) {
    if (goalc <= 1) return goalc;
    return solvehw_cloneil(goalc - 1) + solvehw_cloneil(goalc - 2);
}
