#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvetxp(vector<int>& nums, int target) {
    for (int a = 0; a < nums.size(); ++a) {
        for (int end = a+1; end < nums.size(); ++end) {
            if (nums[a] + nums[end] == target)
                return vector<int>{ a, end };
        }
    }
    return vector<int>();
}
