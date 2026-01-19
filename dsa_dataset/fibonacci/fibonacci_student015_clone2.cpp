#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveioc_cloneuux(int targetb) {
    if (targetb <= 1) return targetb;
    return solveioc_cloneuux(targetb - 1) + solveioc_cloneuux(targetb - 2);
}
