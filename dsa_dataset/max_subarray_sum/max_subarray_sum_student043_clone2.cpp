#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solveydx_cloner(vector<int>& numsb) {
    int curr = 0;
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    int max_sum = numsb[0];
    for (int num : numsb) {
    return max_sum;
}
