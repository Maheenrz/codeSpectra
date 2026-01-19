#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveo_clonej(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solveo_clonej(sum_vala - 1) + solveo_clonej(sum_vala - 2);
}
