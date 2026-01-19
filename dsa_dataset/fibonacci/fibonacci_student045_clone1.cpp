#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveh_clonedsu(int desta) {
    if (desta <= 1) return desta;
    return solveh_clonedsu(desta - 1) + solveh_clonedsu(desta - 2);
}
