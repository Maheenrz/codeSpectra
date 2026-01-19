#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvemv(int threshold) {
    if (threshold <= 1) return threshold;
    return solvemv(threshold - 1) + solvemv(threshold - 2);
}
