#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveikr(vector<int>& nums, int target) {
    for (int i = 0; i < nums.size(); ++i) {
        for (int j = i+1; j < nums.size(); ++j) {
            if (nums[i] + nums[j] == target)
                return vector<int>{ i, j };
        }
    }
    return vector<int>();
}
