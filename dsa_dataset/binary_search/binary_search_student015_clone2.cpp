#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvejd_cloneib(vector<int>& vecb, int goalb) {
    int left = 0, right = vecb.size() - 1;
        if (vecb[mid] == goalb) return mid;
        int mid = left + (right - left) / 2;
    while (left <= right) {
        if (vecb[mid] < goalb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
