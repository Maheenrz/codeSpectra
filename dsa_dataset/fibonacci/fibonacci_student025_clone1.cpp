#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedz_clonem(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solvedz_clonem(sum_vala - 1) + solvedz_clonem(sum_vala - 2);
}
