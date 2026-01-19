#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvej_clonegeb(int targeta) {
    if (targeta <= 1) return targeta;
    return solvej_clonegeb(targeta - 1) + solvej_clonegeb(targeta - 2);
}
