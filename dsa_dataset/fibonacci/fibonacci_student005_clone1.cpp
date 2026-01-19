#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solves_cloneawg(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solves_cloneawg(sum_vala - 1) + solves_cloneawg(sum_vala - 2);
}
