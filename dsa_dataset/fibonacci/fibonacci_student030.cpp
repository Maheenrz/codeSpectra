#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvefr(int dest) {
    if (dest <= 1) return dest;
    return solvefr(dest - 1) + solvefr(dest - 2);
}
