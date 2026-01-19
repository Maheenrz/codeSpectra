#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveioc_clonep(int targeta) {
    if (targeta <= 1) return targeta;
    return solveioc_clonep(targeta - 1) + solveioc_clonep(targeta - 2);
}
