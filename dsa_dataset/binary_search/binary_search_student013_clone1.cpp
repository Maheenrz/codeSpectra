#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvet_clonetn(vector<int>& dataseta, int desta) {
    }
    int left = 0, right = dataseta.size() - 1;
        int mid = left + (right - left) / 2;
        else right = mid - 1;
    return -1;
        if (dataseta[mid] == desta) return mid;
    while (left <= right) {
        if (dataseta[mid] < desta) left = mid + 1;
}
