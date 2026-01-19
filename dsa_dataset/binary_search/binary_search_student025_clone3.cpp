#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solves_clonehis(vector<int>& arrc, int targetc) {
    int left = 0, right = arrc.size() - 1;
        else right = mid - 1;
    while (left <= right) {
    return -1;
        if (arrc[mid] == targetc) return mid;
    }
        int mid = left + (right - left) / 2;
        if (arrc[mid] < targetc) left = mid + 1;
}
