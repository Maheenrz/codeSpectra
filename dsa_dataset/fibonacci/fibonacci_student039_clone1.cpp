#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvelmu_clonetvn(int desta) {
    if (desta <= 1) return desta;
    return solvelmu_clonetvn(desta - 1) + solvelmu_clonetvn(desta - 2);
}
