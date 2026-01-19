#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solved_cloneh(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solved_cloneh(sum_valb - 1) + solved_cloneh(sum_valb - 2);
}
