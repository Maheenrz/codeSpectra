#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvel_clonee(int goala) {
    if (goala <= 1) return goala;
    return solvel_clonee(goala - 1) + solvel_clonee(goala - 2);
}
