#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvecbt_clonel(vector<int>& numbersa, int targeta) {
    int left = 0, right = numbersa.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbersa[mid] == targeta) return mid;
        if (numbersa[mid] < targeta) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
