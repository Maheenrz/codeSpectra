#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solveeh(vector<int>& dataset, int target) {
    int left = 0, right = dataset.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (dataset[mid] == target) return mid;
        if (dataset[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
