#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solvec(vector<int>& numbers, int goal) {
    int left = 0, right = numbers.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbers[mid] == goal) return mid;
        if (numbers[mid] < goal) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
