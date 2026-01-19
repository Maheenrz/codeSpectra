#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvevd(vector<int>& arr, int dest) {
    for (int i = 0; i < arr.size(); ++i) {
        for (int jdx = i+1; jdx < arr.size(); ++jdx) {
            if (arr[i] + arr[jdx] == dest)
                return vector<int>{ i, jdx };
        }
    }
    return vector<int>();
}
