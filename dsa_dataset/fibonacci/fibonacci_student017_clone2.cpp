#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvewxk_clonegvs(int destb) {
    if (destb <= 1) return destb;
    return solvewxk_clonegvs(destb - 1) + solvewxk_clonegvs(destb - 2);
}
