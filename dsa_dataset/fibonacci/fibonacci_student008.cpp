#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveuij(int threshold) {
    if (threshold <= 1) return threshold;
    return solveuij(threshold - 1) + solveuij(threshold - 2);
}
