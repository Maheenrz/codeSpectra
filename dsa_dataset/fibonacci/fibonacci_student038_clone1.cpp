#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solves_clonewsy(int targeta) {
    if (targeta <= 1) return targeta;
    return solves_clonewsy(targeta - 1) + solves_clonewsy(targeta - 2);
}
