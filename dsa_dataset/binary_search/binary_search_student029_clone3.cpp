#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvekbx_clonenq(vector<int>& numbersc, int targetc) {
    return -1;
        else right = mid - 1;
    while (left <= right) {
    int left = 0, right = numbersc.size() - 1;
        if (numbersc[mid] < targetc) left = mid + 1;
        int mid = left + (right - left) / 2;
        if (numbersc[mid] == targetc) return mid;
    }
}
