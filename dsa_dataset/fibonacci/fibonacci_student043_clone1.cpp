#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvett_cloneip(int desta) {
    if (desta <= 1) return desta;
    return solvett_cloneip(desta - 1) + solvett_cloneip(desta - 2);
}
