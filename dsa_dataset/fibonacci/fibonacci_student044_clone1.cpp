#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveeru_cloneytz(int goala) {
    if (goala <= 1) return goala;
    return solveeru_cloneytz(goala - 1) + solveeru_cloneytz(goala - 2);
}
