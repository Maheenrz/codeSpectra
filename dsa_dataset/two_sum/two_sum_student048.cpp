#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedd(vector<int>& vec, int target) {
    for (int i = 0; i < vec.size(); ++i) {
        for (int end = i+1; end < vec.size(); ++end) {
            if (vec[i] + vec[end] == target)
                return vector<int>{ i, end };
        }
    }
    return vector<int>();
}
