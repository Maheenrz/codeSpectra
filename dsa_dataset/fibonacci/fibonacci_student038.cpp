#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solves(int target) {
    if (target <= 1) return target;
    return solves(target - 1) + solves(target - 2);
}
