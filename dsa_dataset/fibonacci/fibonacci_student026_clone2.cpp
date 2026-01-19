#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvertg_clonep(int goalb) {
    if (goalb <= 1) return goalb;
    return solvertg_clonep(goalb - 1) + solvertg_clonep(goalb - 2);
}
