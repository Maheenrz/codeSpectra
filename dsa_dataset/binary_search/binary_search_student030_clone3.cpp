#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveu_clonefnr(vector<int>& numbersc, int thresholdc) {
        else right = mid - 1;
    while (left <= right) {
    int left = 0, right = numbersc.size() - 1;
    }
        if (numbersc[mid] == thresholdc) return mid;
        if (numbersc[mid] < thresholdc) left = mid + 1;
    return -1;
        int mid = left + (right - left) / 2;
}
