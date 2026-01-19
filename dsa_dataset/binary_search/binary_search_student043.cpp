#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solveun(vector<int>& arr, int goal) {
    int left = 0, right = arr.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == goal) return mid;
        if (arr[mid] < goal) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
