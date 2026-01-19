#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveyp(vector<int>& dataset, int sum_val) {
    for (int start = 0; start < dataset.size(); ++start) {
        for (int jdx = start+1; jdx < dataset.size(); ++jdx) {
            if (dataset[start] + dataset[jdx] == sum_val)
                return vector<int>{ start, jdx };
        }
    }
    return vector<int>();
}
