#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedal_cloneg(int destb) {
    if (destb <= 1) return destb;
    return solvedal_cloneg(destb - 1) + solvedal_cloneg(destb - 2);
}
