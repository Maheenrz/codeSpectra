#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecww_clonelx(int desta) {
    if (desta <= 1) return desta;
    return solvecww_clonelx(desta - 1) + solvecww_clonelx(desta - 2);
}
