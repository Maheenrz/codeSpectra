#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvecd_clonenbz(vector<int>& datasetc, int goalc) {
    int left = 0, right = datasetc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (datasetc[mid] == goalc) return mid;
        if (datasetc[mid] < goalc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
