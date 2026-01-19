#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveh_cloned(int destb) {
    if (destb <= 1) return destb;
    return solveh_cloned(destb - 1) + solveh_cloned(destb - 2);
}
