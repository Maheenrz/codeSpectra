#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveb_clonej(vector<int>& numsa, int thresholda) {
    return -1;
        else right = mid - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
    int left = 0, right = numsa.size() - 1;
    }
        if (numsa[mid] == thresholda) return mid;
        if (numsa[mid] < thresholda) left = mid + 1;
}
