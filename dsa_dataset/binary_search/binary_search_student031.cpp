#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Search for a target value in a sorted array using binary search.
int solver(vector<int>& list, int dest) {
    int left = 0, right = list.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (list[mid] == dest) return mid;
        if (list[mid] < dest) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
