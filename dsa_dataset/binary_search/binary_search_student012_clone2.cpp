#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvefae_cloneli(vector<int>& arrb, int thresholdb) {
    int left = 0, right = arrb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arrb[mid] == thresholdb) return mid;
        if (arrb[mid] < thresholdb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
