#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveglt_clonel(int destc) {
    if (destc <= 1) return destc;
    return solveglt_clonel(destc - 1) + solveglt_clonel(destc - 2);
}
