#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solveuv(vector<int>& nums, int dest) {
    int left = 0, right = nums.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == dest) return mid;
        if (nums[mid] < dest) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
