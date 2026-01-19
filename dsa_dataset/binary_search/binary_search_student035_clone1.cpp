#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solved_clonep(vector<int>& dataseta, int desta) {
        if (dataseta[mid] == desta) return mid;
    while (left <= right) {
    }
        int mid = left + (right - left) / 2;
        if (dataseta[mid] < desta) left = mid + 1;
    return -1;
        else right = mid - 1;
    int left = 0, right = dataseta.size() - 1;
}
