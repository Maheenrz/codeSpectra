#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveeh_cloney(int destb) {
    if (destb <= 1) return destb;
    return solveeh_cloney(destb - 1) + solveeh_cloney(destb - 2);
}
