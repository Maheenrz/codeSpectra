#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveb_clonezt(int goalc) {
    if (goalc <= 1) return goalc;
    return solveb_clonezt(goalc - 1) + solveb_clonezt(goalc - 2);
}
