#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solves_cloner(int targetb) {
    if (targetb <= 1) return targetb;
    return solves_cloner(targetb - 1) + solves_cloner(targetb - 2);
}
