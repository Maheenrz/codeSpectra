#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvertg_cloned(int goala) {
    if (goala <= 1) return goala;
    return solvertg_cloned(goala - 1) + solvertg_cloned(goala - 2);
}
