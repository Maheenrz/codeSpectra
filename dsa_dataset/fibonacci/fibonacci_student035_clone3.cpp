#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefen_clonezsg(int targetc) {
    if (targetc <= 1) return targetc;
    return solvefen_clonezsg(targetc - 1) + solvefen_clonezsg(targetc - 2);
}
