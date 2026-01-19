#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveuj(vector<int>& arr, int sum_val) {
    for (int first = 0; first < arr.size(); ++first) {
        for (int end = first+1; end < arr.size(); ++end) {
            if (arr[first] + arr[end] == sum_val)
                return vector<int>{ first, end };
        }
    }
    return vector<int>();
}
