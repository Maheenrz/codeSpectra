#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvee_cloneg(int desta) {
    if (desta <= 1) return desta;
    return solvee_cloneg(desta - 1) + solvee_cloneg(desta - 2);
}
