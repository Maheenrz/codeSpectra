#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveo_clonecm(vector<int>& datasetb, int destb) {
        else right = mid - 1;
    }
    int left = 0, right = datasetb.size() - 1;
        int mid = left + (right - left) / 2;
    return -1;
        if (datasetb[mid] == destb) return mid;
    while (left <= right) {
        if (datasetb[mid] < destb) left = mid + 1;
}
