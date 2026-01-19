#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefen_cloneo(int targetb) {
    if (targetb <= 1) return targetb;
    return solvefen_cloneo(targetb - 1) + solvefen_cloneo(targetb - 2);
}
