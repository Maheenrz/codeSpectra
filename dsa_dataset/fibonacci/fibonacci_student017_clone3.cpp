#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvewxk_clonesx(int destc) {
    if (destc <= 1) return destc;
    return solvewxk_clonesx(destc - 1) + solvewxk_clonesx(destc - 2);
}
