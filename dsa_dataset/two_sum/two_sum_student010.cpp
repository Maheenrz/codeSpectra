#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveycb(vector<int>& nums, int sum_val) {
    for (int a = 0; a < nums.size(); ++a) {
        for (int jdx = a+1; jdx < nums.size(); ++jdx) {
            if (nums[a] + nums[jdx] == sum_val)
                return vector<int>{ a, jdx };
        }
    }
    return vector<int>();
}
