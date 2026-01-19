#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefam_clonedr(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solvefam_clonedr(sum_vala - 1) + solvefam_clonedr(sum_vala - 2);
}
