#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solvecbt(vector<int>& numbers, int target) {
    int left = 0, right = numbers.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbers[mid] == target) return mid;
        if (numbers[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
