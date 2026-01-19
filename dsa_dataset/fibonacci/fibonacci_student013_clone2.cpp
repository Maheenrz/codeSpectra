#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveo_cloner(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solveo_cloner(sum_valb - 1) + solveo_cloner(sum_valb - 2);
}
