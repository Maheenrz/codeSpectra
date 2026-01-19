#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedal_cloneug(int desta) {
    if (desta <= 1) return desta;
    return solvedal_cloneug(desta - 1) + solvedal_cloneug(desta - 2);
}
