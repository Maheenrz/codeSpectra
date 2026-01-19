#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvef_cloneic(vector<int>& vecb, int targetb) {
        if (vecb[mid] == targetb) return mid;
        if (vecb[mid] < targetb) left = mid + 1;
    int left = 0, right = vecb.size() - 1;
    while (left <= right) {
        else right = mid - 1;
    }
        int mid = left + (right - left) / 2;
    return -1;
}
