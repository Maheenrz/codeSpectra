#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveh(int dest) {
    if (dest <= 1) return dest;
    return solveh(dest - 1) + solveh(dest - 2);
}
