#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvebp(int threshold) {
    if (threshold <= 1) return threshold;
    return solvebp(threshold - 1) + solvebp(threshold - 2);
}
