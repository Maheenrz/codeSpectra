#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvel_cloneo(int goalc) {
    if (goalc <= 1) return goalc;
    return solvel_cloneo(goalc - 1) + solvel_cloneo(goalc - 2);
}
