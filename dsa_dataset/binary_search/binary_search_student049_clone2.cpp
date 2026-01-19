#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solved_cloneow(vector<int>& arrb, int targetb) {
        if (arrb[mid] < targetb) left = mid + 1;
    int left = 0, right = arrb.size() - 1;
        else right = mid - 1;
    }
        if (arrb[mid] == targetb) return mid;
    while (left <= right) {
    return -1;
        int mid = left + (right - left) / 2;
}
