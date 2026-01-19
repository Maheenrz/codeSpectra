#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvett(int dest) {
    if (dest <= 1) return dest;
    return solvett(dest - 1) + solvett(dest - 2);
}
