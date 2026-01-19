#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveex_clonea(vector<int>& numbersa, int goala) {
    while (left <= right) {
    int left = 0, right = numbersa.size() - 1;
        int mid = left + (right - left) / 2;
    }
        else right = mid - 1;
        if (numbersa[mid] == goala) return mid;
        if (numbersa[mid] < goala) left = mid + 1;
    return -1;
}
