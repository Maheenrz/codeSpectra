#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvezgc_cloneg(int targetb) {
    if (targetb <= 1) return targetb;
    return solvezgc_cloneg(targetb - 1) + solvezgc_cloneg(targetb - 2);
}
