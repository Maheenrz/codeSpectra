#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solves_clonern(int sum_valc) {
    if (sum_valc <= 1) return sum_valc;
    return solves_clonern(sum_valc - 1) + solves_clonern(sum_valc - 2);
}
