#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveb_clonem(vector<int>& numsb, int destb) {
    }
    while (left <= right) {
    int left = 0, right = numsb.size() - 1;
        if (numsb[mid] == destb) return mid;
        else right = mid - 1;
        if (numsb[mid] < destb) left = mid + 1;
    return -1;
        int mid = left + (right - left) / 2;
}
