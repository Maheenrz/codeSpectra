#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvelmu(int dest) {
    if (dest <= 1) return dest;
    return solvelmu(dest - 1) + solvelmu(dest - 2);
}
