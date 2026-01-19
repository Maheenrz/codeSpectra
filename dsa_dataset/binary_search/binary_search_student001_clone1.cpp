#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solven_cloneo(vector<int>& veca, int goala) {
    while (left <= right) {
    }
        int mid = left + (right - left) / 2;
    int left = 0, right = veca.size() - 1;
        else right = mid - 1;
        if (veca[mid] == goala) return mid;
    return -1;
        if (veca[mid] < goala) left = mid + 1;
}
