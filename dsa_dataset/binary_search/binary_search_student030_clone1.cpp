#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveu_clonefh(vector<int>& numbersa, int thresholda) {
    while (left <= right) {
        if (numbersa[mid] == thresholda) return mid;
        int mid = left + (right - left) / 2;
    int left = 0, right = numbersa.size() - 1;
        if (numbersa[mid] < thresholda) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
