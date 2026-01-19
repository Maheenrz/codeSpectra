#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveex_clonena(vector<int>& numbersc, int goalc) {
    int left = 0, right = numbersc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbersc[mid] == goalc) return mid;
        if (numbersc[mid] < goalc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
