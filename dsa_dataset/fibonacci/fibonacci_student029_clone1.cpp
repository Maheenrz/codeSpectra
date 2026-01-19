#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefq_clonewoe(int targeta) {
    if (targeta <= 1) return targeta;
    return solvefq_clonewoe(targeta - 1) + solvefq_clonewoe(targeta - 2);
}
