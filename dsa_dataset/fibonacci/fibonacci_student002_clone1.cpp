#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvej_cloneou(int targeta) {
    if (targeta <= 1) return targeta;
    return solvej_cloneou(targeta - 1) + solvej_cloneou(targeta - 2);
}
