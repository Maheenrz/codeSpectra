#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveqjh_cloneu(vector<int>& veca, int goala) {
    int left = 0, right = veca.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (veca[mid] == goala) return mid;
        if (veca[mid] < goala) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
