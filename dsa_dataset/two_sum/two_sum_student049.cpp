#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvew(vector<int>& arr, int goal) {
    for (int idx = 0; idx < arr.size(); ++idx) {
        for (int j = idx+1; j < arr.size(); ++j) {
            if (arr[idx] + arr[j] == goal)
                return vector<int>{ idx, j };
        }
    }
    return vector<int>();
}
