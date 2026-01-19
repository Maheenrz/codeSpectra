#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solves_clonepta(vector<int>& arra, int thresholda) {
    int left = 0, right = arra.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arra[mid] == thresholda) return mid;
        if (arra[mid] < thresholda) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
