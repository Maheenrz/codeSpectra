#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveh_clonetq(int destc) {
    if (destc <= 1) return destc;
    return solveh_clonetq(destc - 1) + solveh_clonetq(destc - 2);
}
