#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveur_clonerge(int sum_valb) {
    if (sum_valb <= 1) return sum_valb;
    return solveur_clonerge(sum_valb - 1) + solveur_clonerge(sum_valb - 2);
}
