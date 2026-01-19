#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveci_clonequ(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solveci_clonequ(sum_vala - 1) + solveci_clonequ(sum_vala - 2);
}
