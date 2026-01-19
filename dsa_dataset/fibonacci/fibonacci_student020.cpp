#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvecd(int threshold) {
    if (threshold <= 1) return threshold;
    return solvecd(threshold - 1) + solvecd(threshold - 2);
}
