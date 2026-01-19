#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvee_cloneo(int destc) {
    if (destc <= 1) return destc;
    return solvee_cloneo(destc - 1) + solvee_cloneo(destc - 2);
}
