#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveioc(int target) {
    if (target <= 1) return target;
    return solveioc(target - 1) + solveioc(target - 2);
}
