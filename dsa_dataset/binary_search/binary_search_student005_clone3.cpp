#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvey_clonewbv(vector<int>& numsc, int destc) {
        else right = mid - 1;
        int mid = left + (right - left) / 2;
        if (numsc[mid] < destc) left = mid + 1;
    while (left <= right) {
    return -1;
        if (numsc[mid] == destc) return mid;
    int left = 0, right = numsc.size() - 1;
    }
}
