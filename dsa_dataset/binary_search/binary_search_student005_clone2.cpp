#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvey_cloneli(vector<int>& numsb, int destb) {
    int left = 0, right = numsb.size() - 1;
        int mid = left + (right - left) / 2;
        if (numsb[mid] == destb) return mid;
        if (numsb[mid] < destb) left = mid + 1;
    return -1;
    while (left <= right) {
    }
        else right = mid - 1;
}
