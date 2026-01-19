#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveunz(int threshold) {
    if (threshold <= 1) return threshold;
    return solveunz(threshold - 1) + solveunz(threshold - 2);
}
