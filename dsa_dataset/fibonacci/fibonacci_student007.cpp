#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solvel(int goal) {
    if (goal <= 1) return goal;
    return solvel(goal - 1) + solvel(goal - 2);
}
