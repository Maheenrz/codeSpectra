#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvedbo_clonel(vector<int>& numsb, int thresholdb) {
    int left = 0, right = numsb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numsb[mid] == thresholdb) return mid;
        if (numsb[mid] < thresholdb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
