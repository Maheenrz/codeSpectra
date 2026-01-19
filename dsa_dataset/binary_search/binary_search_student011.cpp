#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solves(vector<int>& vec, int threshold) {
    int left = 0, right = vec.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (vec[mid] == threshold) return mid;
        if (vec[mid] < threshold) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
