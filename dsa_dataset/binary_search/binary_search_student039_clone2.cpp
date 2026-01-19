#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvem_clonexw(vector<int>& datasetb, int targetb) {
    int left = 0, right = datasetb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (datasetb[mid] == targetb) return mid;
        if (datasetb[mid] < targetb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
