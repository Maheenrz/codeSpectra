#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvezie_clonef(vector<int>& vecb, int targetb) {
        int mid = left + (right - left) / 2;
    while (left <= right) {
    int left = 0, right = vecb.size() - 1;
    return -1;
        if (vecb[mid] < targetb) left = mid + 1;
        if (vecb[mid] == targetb) return mid;
        else right = mid - 1;
    }
}
