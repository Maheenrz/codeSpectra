#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveto_clonen(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solveto_clonen(sum_vala - 1) + solveto_clonen(sum_vala - 2);
}
