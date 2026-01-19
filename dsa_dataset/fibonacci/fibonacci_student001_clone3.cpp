#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvenhn_cloneqz(int goalc) {
    if (goalc <= 1) return goalc;
    return solvenhn_cloneqz(goalc - 1) + solvenhn_cloneqz(goalc - 2);
}
