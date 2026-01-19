#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveql_clonevo(int thresholdb) {
    if (thresholdb <= 1) return thresholdb;
    return solveql_clonevo(thresholdb - 1) + solveql_clonevo(thresholdb - 2);
}
