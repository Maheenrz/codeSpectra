#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvecmn(int threshold) {
    if (threshold <= 1) return threshold;
    return solvecmn(threshold - 1) + solvecmn(threshold - 2);
}
