#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvevk(int threshold) {
    if (threshold <= 1) return threshold;
    return solvevk(threshold - 1) + solvevk(threshold - 2);
}
