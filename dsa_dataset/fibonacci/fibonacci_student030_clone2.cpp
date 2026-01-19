#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefr_clonezz(int destb) {
    if (destb <= 1) return destb;
    return solvefr_clonezz(destb - 1) + solvefr_clonezz(destb - 2);
}
