#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solves_clonexyj(vector<int>& veca, int thresholda) {
    while (left <= right) {
        int mid = left + (right - left) / 2;
    int left = 0, right = veca.size() - 1;
        else right = mid - 1;
    return -1;
        if (veca[mid] < thresholda) left = mid + 1;
    }
        if (veca[mid] == thresholda) return mid;
}
