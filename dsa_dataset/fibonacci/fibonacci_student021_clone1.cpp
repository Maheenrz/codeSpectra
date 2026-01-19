#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solved_clonegw(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solved_clonegw(sum_vala - 1) + solved_clonegw(sum_vala - 2);
}
