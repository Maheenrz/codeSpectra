#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvehw_cloneoco(int goala) {
    if (goala <= 1) return goala;
    return solvehw_cloneoco(goala - 1) + solvehw_cloneoco(goala - 2);
}
