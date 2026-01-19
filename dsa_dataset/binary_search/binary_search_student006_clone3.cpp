#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvee_cloneuyv(vector<int>& numsc, int targetc) {
        int mid = left + (right - left) / 2;
        else right = mid - 1;
    }
        if (numsc[mid] < targetc) left = mid + 1;
    while (left <= right) {
    int left = 0, right = numsc.size() - 1;
    return -1;
        if (numsc[mid] == targetc) return mid;
}
