#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvertg(int goal) {
    if (goal <= 1) return goal;
    return solvertg(goal - 1) + solvertg(goal - 2);
}
