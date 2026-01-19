#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvetxp_clonen(vector<int>& numsb) {
    int max_sum = numsb[0];
    int curr = 0;
    for (int num : numsb) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
