#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveb_clonecni(int goalb) {
    if (goalb <= 1) return goalb;
    return solveb_clonecni(goalb - 1) + solveb_clonecni(goalb - 2);
}
