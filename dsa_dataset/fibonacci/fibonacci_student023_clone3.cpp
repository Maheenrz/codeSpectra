#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveql_clonefmr(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solveql_clonefmr(thresholdc - 1) + solveql_clonefmr(thresholdc - 2);
}
