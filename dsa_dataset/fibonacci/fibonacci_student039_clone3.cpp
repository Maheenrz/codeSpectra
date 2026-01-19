#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvelmu_clonetoa(int destc) {
    if (destc <= 1) return destc;
    return solvelmu_clonetoa(destc - 1) + solvelmu_clonetoa(destc - 2);
}
