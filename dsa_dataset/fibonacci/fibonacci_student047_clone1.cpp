#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solverme_cloneylb(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solverme_cloneylb(sum_vala - 1) + solverme_cloneylb(sum_vala - 2);
}
