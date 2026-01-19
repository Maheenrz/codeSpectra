#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvehj_clonee(vector<int>& dataseta, int desta) {
    int left = 0, right = dataseta.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (dataseta[mid] == desta) return mid;
        if (dataseta[mid] < desta) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
