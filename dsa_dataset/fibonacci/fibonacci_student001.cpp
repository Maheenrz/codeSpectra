#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvenhn(int goal) {
    if (goal <= 1) return goal;
    return solvenhn(goal - 1) + solvenhn(goal - 2);
}
