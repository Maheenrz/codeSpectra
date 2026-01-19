#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvenhn_clonev(int goala) {
    if (goala <= 1) return goala;
    return solvenhn_clonev(goala - 1) + solvenhn_clonev(goala - 2);
}
