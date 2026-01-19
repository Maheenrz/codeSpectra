#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvekvu(int threshold) {
    if (threshold <= 1) return threshold;
    return solvekvu(threshold - 1) + solvekvu(threshold - 2);
}
