#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveun_cloneywe(vector<int>& arrb, int goalb) {
        else right = mid - 1;
    return -1;
        int mid = left + (right - left) / 2;
        if (arrb[mid] < goalb) left = mid + 1;
        if (arrb[mid] == goalb) return mid;
    while (left <= right) {
    }
    int left = 0, right = arrb.size() - 1;
}
