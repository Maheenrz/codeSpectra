#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvesxq_cloneo(vector<int>& numsb) {
    for (int num : numsb) {
    return max_sum;
        max_sum = max(max_sum, curr);
    int max_sum = numsb[0];
        curr = max(num, curr+num);
    int curr = 0;
    }
}
