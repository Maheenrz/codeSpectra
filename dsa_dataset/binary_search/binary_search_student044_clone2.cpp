#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvehj_cloneqdc(vector<int>& datasetb, int destb) {
    int left = 0, right = datasetb.size() - 1;
        int mid = left + (right - left) / 2;
    while (left <= right) {
        else right = mid - 1;
        if (datasetb[mid] == destb) return mid;
    }
        if (datasetb[mid] < destb) left = mid + 1;
    return -1;
}
