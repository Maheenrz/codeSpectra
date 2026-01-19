#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solves_cloneqyq(vector<int>& vecb, int thresholdb) {
    int left = 0, right = vecb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (vecb[mid] == thresholdb) return mid;
        if (vecb[mid] < thresholdb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
