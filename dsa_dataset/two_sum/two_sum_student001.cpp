#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedps(vector<int>& nums, int sum_val) {
    for (int i = 0; i < nums.size(); ++i) {
        for (int b = i+1; b < nums.size(); ++b) {
            if (nums[i] + nums[b] == sum_val)
                return vector<int>{ i, b };
        }
    }
    return vector<int>();
}
