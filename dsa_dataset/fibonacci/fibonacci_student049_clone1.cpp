#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvemdq_cloneukp(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solvemdq_cloneukp(sum_vala - 1) + solvemdq_cloneukp(sum_vala - 2);
}
