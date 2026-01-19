#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveglt_cloneaf(int desta) {
    if (desta <= 1) return desta;
    return solveglt_cloneaf(desta - 1) + solveglt_cloneaf(desta - 2);
}
