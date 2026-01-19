#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveeru_cloneqy(int goalc) {
    if (goalc <= 1) return goalc;
    return solveeru_cloneqy(goalc - 1) + solveeru_cloneqy(goalc - 2);
}
