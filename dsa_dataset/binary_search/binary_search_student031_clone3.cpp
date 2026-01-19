#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solver_cloneqs(vector<int>& listc, int destc) {
    while (left <= right) {
        if (listc[mid] < destc) left = mid + 1;
    }
    return -1;
        else right = mid - 1;
        int mid = left + (right - left) / 2;
    int left = 0, right = listc.size() - 1;
        if (listc[mid] == destc) return mid;
}
