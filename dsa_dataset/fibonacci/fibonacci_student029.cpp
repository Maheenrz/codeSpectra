#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvefq(int target) {
    if (target <= 1) return target;
    return solvefq(target - 1) + solvefq(target - 2);
}
