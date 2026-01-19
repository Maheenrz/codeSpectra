#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvevhm(vector<int>& dataset, int dest) {
    for (int i = 0; i < dataset.size(); ++i) {
        for (int jdx = i+1; jdx < dataset.size(); ++jdx) {
            if (dataset[i] + dataset[jdx] == dest)
                return vector<int>{ i, jdx };
        }
    }
    return vector<int>();
}
