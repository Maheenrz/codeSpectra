#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvenuc(vector<int>& arr, int target) {
    for (int start = 0; start < arr.size(); ++start) {
        for (int end = start+1; end < arr.size(); ++end) {
            if (arr[start] + arr[end] == target)
                return vector<int>{ start, end };
        }
    }
    return vector<int>();
}
