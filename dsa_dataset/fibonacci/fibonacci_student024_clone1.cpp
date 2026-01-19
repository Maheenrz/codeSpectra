#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solveb_clonem(int goala) {
    if (goala <= 1) return goala;
    return solveb_clonem(goala - 1) + solveb_clonem(goala - 2);
}
