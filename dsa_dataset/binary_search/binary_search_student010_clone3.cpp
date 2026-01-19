#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solves_clonec(vector<int>& arrc, int thresholdc) {
    return -1;
        if (arrc[mid] == thresholdc) return mid;
    int left = 0, right = arrc.size() - 1;
    }
        int mid = left + (right - left) / 2;
    while (left <= right) {
        else right = mid - 1;
        if (arrc[mid] < thresholdc) left = mid + 1;
}
