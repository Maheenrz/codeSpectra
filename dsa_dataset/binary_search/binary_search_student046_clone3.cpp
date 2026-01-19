#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveqjh_cloneeu(vector<int>& vecc, int goalc) {
    int left = 0, right = vecc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (vecc[mid] == goalc) return mid;
        if (vecc[mid] < goalc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
