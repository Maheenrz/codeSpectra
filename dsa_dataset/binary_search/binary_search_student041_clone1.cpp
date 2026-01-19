#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveb_clonepi(vector<int>& numsa, int desta) {
        int mid = left + (right - left) / 2;
        if (numsa[mid] < desta) left = mid + 1;
    return -1;
    while (left <= right) {
    }
    int left = 0, right = numsa.size() - 1;
        if (numsa[mid] == desta) return mid;
        else right = mid - 1;
}
