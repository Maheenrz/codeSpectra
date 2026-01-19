#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveyhg(vector<int>& nums, int sum_val) {
    for (int a = 0; a < nums.size(); ++a) {
        for (int end = a+1; end < nums.size(); ++end) {
            if (nums[a] + nums[end] == sum_val)
                return vector<int>{ a, end };
        }
    }
    return vector<int>();
}
