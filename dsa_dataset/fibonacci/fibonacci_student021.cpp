#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Compute the Nth Fibonacci number.
int solved(int sum_val) {
    if (sum_val <= 1) return sum_val;
    return solved(sum_val - 1) + solved(sum_val - 2);
}
