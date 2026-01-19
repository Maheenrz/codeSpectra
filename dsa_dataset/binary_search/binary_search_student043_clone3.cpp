#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveun_clonejm(vector<int>& arrc, int goalc) {
    while (left <= right) {
    int left = 0, right = arrc.size() - 1;
    return -1;
        int mid = left + (right - left) / 2;
        else right = mid - 1;
        if (arrc[mid] < goalc) left = mid + 1;
    }
        if (arrc[mid] == goalc) return mid;
}
