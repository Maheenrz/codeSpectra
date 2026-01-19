#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveeru_clonez(int goalb) {
    if (goalb <= 1) return goalb;
    return solveeru_clonez(goalb - 1) + solveeru_clonez(goalb - 2);
}
