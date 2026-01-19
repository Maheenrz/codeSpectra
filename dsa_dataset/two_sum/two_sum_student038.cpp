#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvehcd(vector<int>& arr, int sum_val) {
    for (int idx = 0; idx < arr.size(); ++idx) {
        for (int jdx = idx+1; jdx < arr.size(); ++jdx) {
            if (arr[idx] + arr[jdx] == sum_val)
                return vector<int>{ idx, jdx };
        }
    }
    return vector<int>();
}
