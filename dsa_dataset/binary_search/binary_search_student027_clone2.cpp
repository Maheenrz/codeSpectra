#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvecd_clonei(vector<int>& datasetb, int goalb) {
    int left = 0, right = datasetb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (datasetb[mid] == goalb) return mid;
        if (datasetb[mid] < goalb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
