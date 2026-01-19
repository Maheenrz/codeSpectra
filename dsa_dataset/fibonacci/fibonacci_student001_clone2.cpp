#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvenhn_clonecau(int goalb) {
    if (goalb <= 1) return goalb;
    return solvenhn_clonecau(goalb - 1) + solvenhn_clonecau(goalb - 2);
}
