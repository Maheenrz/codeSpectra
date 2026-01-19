#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedhc(vector<int>& arr, int dest) {
    for (int idx = 0; idx < arr.size(); ++idx) {
        for (int second = idx+1; second < arr.size(); ++second) {
            if (arr[idx] + arr[second] == dest)
                return vector<int>{ idx, second };
        }
    }
    return vector<int>();
}
