#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvefh_cloneper(vector<int>& listb, int goalb) {
    int left = 0, right = listb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (listb[mid] == goalb) return mid;
        if (listb[mid] < goalb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
