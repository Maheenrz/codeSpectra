#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveur(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solveur(sum_val - 1) + solveur(sum_val - 2);
}
