#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solvefe(vector<int>& arr, int threshold) {
    int left = 0, right = arr.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == threshold) return mid;
        if (arr[mid] < threshold) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
