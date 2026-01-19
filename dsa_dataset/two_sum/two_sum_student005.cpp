#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefw(vector<int>& dataset, int dest) {
    for (int first = 0; first < dataset.size(); ++first) {
        for (int b = first+1; b < dataset.size(); ++b) {
            if (dataset[first] + dataset[b] == dest)
                return vector<int>{ first, b };
        }
    }
    return vector<int>();
}
