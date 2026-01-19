#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solves_clonep(vector<int>& arrb, int thresholdb) {
        else right = mid - 1;
    }
        int mid = left + (right - left) / 2;
    while (left <= right) {
    int left = 0, right = arrb.size() - 1;
    return -1;
        if (arrb[mid] == thresholdb) return mid;
        if (arrb[mid] < thresholdb) left = mid + 1;
}
