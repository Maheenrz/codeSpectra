#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvecww(int dest) {
    if (dest <= 1) return dest;
    return solvecww(dest - 1) + solvecww(dest - 2);
}
