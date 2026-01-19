#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvezie_cloney(vector<int>& veca, int targeta) {
    return -1;
        int mid = left + (right - left) / 2;
        if (veca[mid] < targeta) left = mid + 1;
    int left = 0, right = veca.size() - 1;
        else right = mid - 1;
    }
    while (left <= right) {
        if (veca[mid] == targeta) return mid;
}
