#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvemv(vector<int>& nums, int dest) {
    for (int first = 0; first < nums.size(); ++first) {
        for (int jdx = first+1; jdx < nums.size(); ++jdx) {
            if (nums[first] + nums[jdx] == dest)
                return vector<int>{ first, jdx };
        }
    }
    return vector<int>();
}
