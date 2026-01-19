#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvea(int dest) {
    if (dest <= 1) return dest;
    return solvea(dest - 1) + solvea(dest - 2);
}
