#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solved_cloneuj(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solved_cloneuj(sum_valc - 1) + solved_cloneuj(sum_valc - 2);
}
