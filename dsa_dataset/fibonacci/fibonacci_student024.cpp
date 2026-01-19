#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solveb(int goal) {
    if (goal <= 1) return goal;
    return solveb(goal - 1) + solveb(goal - 2);
}
