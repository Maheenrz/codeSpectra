#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvewxk_clonekuh(int desta) {
    if (desta <= 1) return desta;
    return solvewxk_clonekuh(desta - 1) + solvewxk_clonekuh(desta - 2);
}
