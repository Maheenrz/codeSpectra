#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvemv_clonegrk(int thresholdc) {
    if (thresholdc <= 1) return thresholdc;
    return solvemv_clonegrk(thresholdc - 1) + solvemv_clonegrk(thresholdc - 2);
}
