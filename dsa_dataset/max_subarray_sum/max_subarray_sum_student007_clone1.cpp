#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvevrn_clonetf(vector<int>& arra) {
    int curr = 0;
    for (int num : arra) {
    return max_sum;
        max_sum = max(max_sum, curr);
    }
        curr = max(num, curr+num);
    int max_sum = arra[0];
}
