#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solvefth(vector<int>& list, int sum_val) {
    int left = 0, right = list.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (list[mid] == sum_val) return mid;
        if (list[mid] < sum_val) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
