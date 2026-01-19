#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvej_clonexpi(int targetb) {
    if (targetb <= 1) return targetb;
    return solvej_clonexpi(targetb - 1) + solvej_clonexpi(targetb - 2);
}
