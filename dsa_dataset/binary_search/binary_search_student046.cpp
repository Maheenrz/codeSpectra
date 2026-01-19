#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solveqjh(vector<int>& vec, int goal) {
    int left = 0, right = vec.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (vec[mid] == goal) return mid;
        if (vec[mid] < goal) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
