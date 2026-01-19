#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvecd_cloneril(vector<int>& dataseta, int goala) {
    while (left <= right) {
    }
        else right = mid - 1;
    int left = 0, right = dataseta.size() - 1;
    return -1;
        int mid = left + (right - left) / 2;
        if (dataseta[mid] < goala) left = mid + 1;
        if (dataseta[mid] == goala) return mid;
}
