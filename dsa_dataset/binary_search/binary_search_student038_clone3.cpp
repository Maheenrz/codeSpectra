#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvezie_cloneovx(vector<int>& vecc, int targetc) {
    int left = 0, right = vecc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (vecc[mid] == targetc) return mid;
        if (vecc[mid] < targetc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
