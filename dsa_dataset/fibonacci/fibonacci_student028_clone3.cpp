#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveeh_clonel(int destc) {
    if (destc <= 1) return destc;
    return solveeh_clonel(destc - 1) + solveeh_clonel(destc - 2);
}
