#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveqvr_cloneo(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solveqvr_cloneo(sum_vala - 1) + solveqvr_cloneo(sum_vala - 2);
}
