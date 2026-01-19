#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvecrt_clonei(vector<int>& veca, int goala) {
        else right = mid - 1;
        if (veca[mid] == goala) return mid;
        if (veca[mid] < goala) left = mid + 1;
        int mid = left + (right - left) / 2;
    }
    return -1;
    while (left <= right) {
    int left = 0, right = veca.size() - 1;
}
