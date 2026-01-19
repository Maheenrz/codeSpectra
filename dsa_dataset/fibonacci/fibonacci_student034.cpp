#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvee(int dest) {
    if (dest <= 1) return dest;
    return solvee(dest - 1) + solvee(dest - 2);
}
