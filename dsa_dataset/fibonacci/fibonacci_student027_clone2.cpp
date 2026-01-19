#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedpn_cloneg(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solvedpn_cloneg(sum_valb - 1) + solvedpn_cloneg(sum_valb - 2);
}
