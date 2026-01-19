#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvefe_cloneo(vector<int>& arrc, int thresholdc) {
    }
        int mid = left + (right - left) / 2;
        if (arrc[mid] < thresholdc) left = mid + 1;
    while (left <= right) {
        if (arrc[mid] == thresholdc) return mid;
        else right = mid - 1;
    int left = 0, right = arrc.size() - 1;
    return -1;
}
