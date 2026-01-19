#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvefen(int target) {
    if (target <= 1) return target;
    return solvefen(target - 1) + solvefen(target - 2);
}
