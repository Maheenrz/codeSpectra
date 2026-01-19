#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solves_cloneyv(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solves_cloneyv(sum_valb - 1) + solves_cloneyv(sum_valb - 2);
}
