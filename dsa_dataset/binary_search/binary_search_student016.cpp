#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solvej(vector<int>& numbers, int sum_val) {
    int left = 0, right = numbers.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbers[mid] == sum_val) return mid;
        if (numbers[mid] < sum_val) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
