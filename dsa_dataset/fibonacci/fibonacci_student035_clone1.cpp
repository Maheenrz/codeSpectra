#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefen_clonec(int targeta) {
    if (targeta <= 1) return targeta;
    return solvefen_clonec(targeta - 1) + solvefen_clonec(targeta - 2);
}
