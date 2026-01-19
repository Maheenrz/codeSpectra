#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvez(vector<int>& nums, int sum_val) {
    for (int first = 0; first < nums.size(); ++first) {
        for (int jdx = first+1; jdx < nums.size(); ++jdx) {
            if (nums[first] + nums[jdx] == sum_val)
                return vector<int>{ first, jdx };
        }
    }
    return vector<int>();
}
