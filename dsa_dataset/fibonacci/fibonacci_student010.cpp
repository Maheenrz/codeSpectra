#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvejhd(int threshold) {
    if (threshold <= 1) return threshold;
    return solvejhd(threshold - 1) + solvejhd(threshold - 2);
}
