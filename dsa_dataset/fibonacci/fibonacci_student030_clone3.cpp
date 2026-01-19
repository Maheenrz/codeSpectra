#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefr_cloneyuc(int destc) {
    if (destc <= 1) return destc;
    return solvefr_cloneyuc(destc - 1) + solvefr_cloneyuc(destc - 2);
}
