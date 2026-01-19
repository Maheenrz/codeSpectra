#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvezfl(vector<int>& vec, int target) {
    for (int i = 0; i < vec.size(); ++i) {
        for (int second = i+1; second < vec.size(); ++second) {
            if (vec[i] + vec[second] == target)
                return vector<int>{ i, second };
        }
    }
    return vector<int>();
}
