#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveur_clonexid(int sum_vala) {
    if (sum_vala <= 1) return sum_vala;
    return solveur_clonexid(sum_vala - 1) + solveur_clonexid(sum_vala - 2);
}
