#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedpn_clonevld(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solvedpn_clonevld(sum_vala - 1) + solvedpn_clonevld(sum_vala - 2);
}
