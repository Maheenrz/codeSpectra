#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvejw(vector<int>& arr, int goal) {
    for (int i = 0; i < arr.size(); ++i) {
        for (int j = i+1; j < arr.size(); ++j) {
            if (arr[i] + arr[j] == goal)
                return vector<int>{ i, j };
        }
    }
    return vector<int>();
}
