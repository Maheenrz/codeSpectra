#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedmg(vector<int>& arr, int sum_val) {
    for (int idx = 0; idx < arr.size(); ++idx) {
        for (int b = idx+1; b < arr.size(); ++b) {
            if (arr[idx] + arr[b] == sum_val)
                return vector<int>{ idx, b };
        }
    }
    return vector<int>();
}
