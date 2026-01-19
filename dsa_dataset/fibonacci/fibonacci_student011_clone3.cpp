#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecww_clonelt(int destc) {
    if (destc <= 1) return destc;
    return solvecww_clonelt(destc - 1) + solvecww_clonelt(destc - 2);
}
