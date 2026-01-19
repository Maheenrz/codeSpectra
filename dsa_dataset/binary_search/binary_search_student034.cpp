#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solveo(vector<int>& dataset, int goal) {
    int left = 0, right = dataset.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (dataset[mid] == goal) return mid;
        if (dataset[mid] < goal) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
