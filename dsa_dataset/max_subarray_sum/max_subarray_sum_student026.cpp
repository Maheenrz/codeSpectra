#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the contiguous subarray with the largest sum.
int solvestz(vector<int>& nums) {
    int max_sum = nums[0];
    int curr = 0;
    for (int num : nums) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
