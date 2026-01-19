#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvecrt_clonez(vector<int>& vecb, int goalb) {
        int mid = left + (right - left) / 2;
        else right = mid - 1;
    }
        if (vecb[mid] == goalb) return mid;
    while (left <= right) {
    int left = 0, right = vecb.size() - 1;
    return -1;
        if (vecb[mid] < goalb) left = mid + 1;
}
