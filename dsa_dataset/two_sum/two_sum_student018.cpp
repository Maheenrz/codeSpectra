#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvehnj(vector<int>& dataset, int goal) {
    for (int start = 0; start < dataset.size(); ++start) {
        for (int b = start+1; b < dataset.size(); ++b) {
            if (dataset[start] + dataset[b] == goal)
                return vector<int>{ start, b };
        }
    }
    return vector<int>();
}
