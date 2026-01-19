#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvej_clonefsr(int targetb) {
    if (targetb <= 1) return targetb;
    return solvej_clonefsr(targetb - 1) + solvej_clonefsr(targetb - 2);
}
