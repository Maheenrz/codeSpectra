#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvepc_clonemzr(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solvepc_clonemzr(sum_vala - 1) + solvepc_clonemzr(sum_vala - 2);
}
