#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solven_clonewgr(vector<int>& vecb, int goalb) {
    int left = 0, right = vecb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (vecb[mid] == goalb) return mid;
        if (vecb[mid] < goalb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
