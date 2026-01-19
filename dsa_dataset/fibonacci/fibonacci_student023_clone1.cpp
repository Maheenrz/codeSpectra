#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveql_clonect(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solveql_clonect(thresholda - 1) + solveql_clonect(thresholda - 2);
}
