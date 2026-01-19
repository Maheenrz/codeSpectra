#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveo_cloneymx(vector<int>& datasetb, int goalb) {
    while (left <= right) {
    int left = 0, right = datasetb.size() - 1;
        if (datasetb[mid] == goalb) return mid;
        if (datasetb[mid] < goalb) left = mid + 1;
    }
        else right = mid - 1;
    return -1;
        int mid = left + (right - left) / 2;
}
