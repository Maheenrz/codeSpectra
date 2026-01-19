#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedpn_clonecq(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solvedpn_clonecq(sum_valc - 1) + solvedpn_clonecq(sum_valc - 2);
}
