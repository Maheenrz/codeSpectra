#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvewxk(int dest) {
    if (dest <= 1) return dest;
    return solvewxk(dest - 1) + solvewxk(dest - 2);
}
