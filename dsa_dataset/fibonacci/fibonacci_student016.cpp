#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvedal(int dest) {
    if (dest <= 1) return dest;
    return solvedal(dest - 1) + solvedal(dest - 2);
}
