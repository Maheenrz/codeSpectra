#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvej(int target) {
    if (target <= 1) return target;
    return solvej(target - 1) + solvej(target - 2);
}
