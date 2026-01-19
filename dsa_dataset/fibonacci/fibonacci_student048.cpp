#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvezgc(int target) {
    if (target <= 1) return target;
    return solvezgc(target - 1) + solvezgc(target - 2);
}
