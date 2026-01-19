#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvey_clonevc(vector<int>& numsa, int desta) {
    return -1;
        if (numsa[mid] == desta) return mid;
    int left = 0, right = numsa.size() - 1;
        else right = mid - 1;
    while (left <= right) {
        if (numsa[mid] < desta) left = mid + 1;
        int mid = left + (right - left) / 2;
    }
}
