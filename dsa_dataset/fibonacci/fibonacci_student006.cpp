#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvehw(int goal) {
    if (goal <= 1) return goal;
    return solvehw(goal - 1) + solvehw(goal - 2);
}
