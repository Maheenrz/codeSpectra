#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvewu_clonegng(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solvewu_clonegng(sum_valb - 1) + solvewu_clonegng(sum_valb - 2);
}
