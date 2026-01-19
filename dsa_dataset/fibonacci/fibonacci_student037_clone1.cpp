#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveiv_clonerbk(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solveiv_clonerbk(sum_vala - 1) + solveiv_clonerbk(sum_vala - 2);
}
