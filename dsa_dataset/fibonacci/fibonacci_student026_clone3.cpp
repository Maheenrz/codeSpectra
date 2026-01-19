#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvertg_clonej(int goalc) {
    if (goalc <= 1) return goalc;
    return solvertg_clonej(goalc - 1) + solvertg_clonej(goalc - 2);
}
