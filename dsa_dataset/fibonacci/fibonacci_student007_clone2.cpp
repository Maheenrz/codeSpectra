#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvel_cloneraf(int goalb) {
    if (goalb <= 1) return goalb;
    return solvel_cloneraf(goalb - 1) + solvel_cloneraf(goalb - 2);
}
