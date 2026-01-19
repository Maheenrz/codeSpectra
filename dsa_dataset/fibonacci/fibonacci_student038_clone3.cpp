#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solves_clonebrx(int targetc) {
    if (targetc <= 1) return targetc;
    return solves_clonebrx(targetc - 1) + solves_clonebrx(targetc - 2);
}
