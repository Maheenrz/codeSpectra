#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solved_cloneoi(vector<int>& datasetb, int destb) {
    int left = 0, right = datasetb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (datasetb[mid] == destb) return mid;
        if (datasetb[mid] < destb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
