#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefu(vector<int>& arr, int sum_val) {
    for (int i = 0; i < arr.size(); ++i) {
        for (int end = i+1; end < arr.size(); ++end) {
            if (arr[i] + arr[end] == sum_val)
                return vector<int>{ i, end };
        }
    }
    return vector<int>();
}
