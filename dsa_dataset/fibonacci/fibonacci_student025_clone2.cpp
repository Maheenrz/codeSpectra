#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvedz_clonejj(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solvedz_clonejj(sum_valb - 1) + solvedz_clonejj(sum_valb - 2);
}
