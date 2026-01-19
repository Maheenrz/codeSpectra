#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveqt_cloneipk(vector<int>& listc, int targetc) {
    int left = 0, right = listc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (listc[mid] == targetc) return mid;
        if (listc[mid] < targetc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
