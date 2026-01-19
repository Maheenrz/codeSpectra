#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveqa(vector<int>& vec, int target) {
    for (int i = 0; i < vec.size(); ++i) {
        for (int jdx = i+1; jdx < vec.size(); ++jdx) {
            if (vec[i] + vec[jdx] == target)
                return vector<int>{ i, jdx };
        }
    }
    return vector<int>();
}
