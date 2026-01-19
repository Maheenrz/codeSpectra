#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvefh_cloneue(vector<int>& listc, int goalc) {
        else right = mid - 1;
    while (left <= right) {
    return -1;
    int left = 0, right = listc.size() - 1;
        int mid = left + (right - left) / 2;
        if (listc[mid] < goalc) left = mid + 1;
        if (listc[mid] == goalc) return mid;
    }
}
