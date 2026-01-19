#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveto_clonegtx(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solveto_clonegtx(sum_valb - 1) + solveto_clonegtx(sum_valb - 2);
}
