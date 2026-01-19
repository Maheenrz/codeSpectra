#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveci_clonefef(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solveci_clonefef(sum_valb - 1) + solveci_clonefef(sum_valb - 2);
}
