#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveiy_clonexcv(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solveiy_clonexcv(sum_valb - 1) + solveiy_clonexcv(sum_valb - 2);
}
