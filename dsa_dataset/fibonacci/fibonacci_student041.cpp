#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveglt(int dest) {
    if (dest <= 1) return dest;
    return solveglt(dest - 1) + solveglt(dest - 2);
}
