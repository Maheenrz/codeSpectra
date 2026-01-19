#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvefr_clonea(int desta) {
    if (desta <= 1) return desta;
    return solvefr_clonea(desta - 1) + solvefr_clonea(desta - 2);
}
