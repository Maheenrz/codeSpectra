#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveeru(int goal) {
    if (goal <= 1) return goal;
    return solveeru(goal - 1) + solveeru(goal - 2);
}
