#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvea_clonekx(int desta) {
    if (desta <= 1) return desta;
    return solvea_clonekx(desta - 1) + solvea_clonekx(desta - 2);
}
