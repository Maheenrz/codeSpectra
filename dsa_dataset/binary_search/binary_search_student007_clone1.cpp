#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveuv_clonekkn(vector<int>& numsa, int desta) {
    }
        int mid = left + (right - left) / 2;
    while (left <= right) {
        if (numsa[mid] < desta) left = mid + 1;
        else right = mid - 1;
        if (numsa[mid] == desta) return mid;
    return -1;
    int left = 0, right = numsa.size() - 1;
}
