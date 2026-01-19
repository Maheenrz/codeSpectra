#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvezgc_clonel(int targeta) {
    if (targeta <= 1) return targeta;
    return solvezgc_clonel(targeta - 1) + solvezgc_clonel(targeta - 2);
}
