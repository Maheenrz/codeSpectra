#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveprj(vector<int>& dataset, int goal) {
    for (int idx = 0; idx < dataset.size(); ++idx) {
        for (int end = idx+1; end < dataset.size(); ++end) {
            if (dataset[idx] + dataset[end] == goal)
                return vector<int>{ idx, end };
        }
    }
    return vector<int>();
}
