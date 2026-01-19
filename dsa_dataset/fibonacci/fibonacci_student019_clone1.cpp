#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvewu_cloneef(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solvewu_cloneef(sum_vala - 1) + solvewu_cloneef(sum_vala - 2);
}
