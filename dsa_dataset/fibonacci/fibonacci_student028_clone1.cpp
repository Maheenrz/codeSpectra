#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveeh_clonez(int desta) {
    if (desta <= 1) return desta;
    return solveeh_clonez(desta - 1) + solveeh_clonez(desta - 2);
}
