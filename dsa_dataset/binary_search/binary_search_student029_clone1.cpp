#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvekbx_clonefdx(vector<int>& numbersa, int targeta) {
        int mid = left + (right - left) / 2;
    while (left <= right) {
        if (numbersa[mid] < targeta) left = mid + 1;
    return -1;
        if (numbersa[mid] == targeta) return mid;
    int left = 0, right = numbersa.size() - 1;
        else right = mid - 1;
    }
}
