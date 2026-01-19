#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefq_cloneob(int targetb) {
    if (targetb <= 1) return targetb;
    return solvefq_cloneob(targetb - 1) + solvefq_cloneob(targetb - 2);
}
