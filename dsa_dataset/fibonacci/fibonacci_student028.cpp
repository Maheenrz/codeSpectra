#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveeh(int dest) {
    if (dest <= 1) return dest;
    return solveeh(dest - 1) + solveeh(dest - 2);
}
