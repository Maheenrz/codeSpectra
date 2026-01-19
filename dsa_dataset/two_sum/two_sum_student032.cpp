#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvery(vector<int>& nums, int dest) {
    for (int start = 0; start < nums.size(); ++start) {
        for (int second = start+1; second < nums.size(); ++second) {
            if (nums[start] + nums[second] == dest)
                return vector<int>{ start, second };
        }
    }
    return vector<int>();
}
