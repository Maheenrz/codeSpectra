#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvem_clonelp(vector<int>& datasetc, int targetc) {
    int left = 0, right = datasetc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (datasetc[mid] == targetc) return mid;
        if (datasetc[mid] < targetc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
