#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvee_clonel(int destb) {
    if (destb <= 1) return destb;
    return solvee_clonel(destb - 1) + solvee_clonel(destb - 2);
}
