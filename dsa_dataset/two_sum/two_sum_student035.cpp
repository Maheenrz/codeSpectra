#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveqo(vector<int>& arr, int dest) {
    for (int a = 0; a < arr.size(); ++a) {
        for (int end = a+1; end < arr.size(); ++end) {
            if (arr[a] + arr[end] == dest)
                return vector<int>{ a, end };
        }
    }
    return vector<int>();
}
