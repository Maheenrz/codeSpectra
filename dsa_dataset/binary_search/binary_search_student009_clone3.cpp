#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveb_clonesj(vector<int>& numsc, int thresholdc) {
    int left = 0, right = numsc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numsc[mid] == thresholdc) return mid;
        if (numsc[mid] < thresholdc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
