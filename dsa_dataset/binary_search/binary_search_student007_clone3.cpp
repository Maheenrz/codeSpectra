#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveuv_clonehz(vector<int>& numsc, int destc) {
    }
    while (left <= right) {
        int mid = left + (right - left) / 2;
    int left = 0, right = numsc.size() - 1;
        else right = mid - 1;
    return -1;
        if (numsc[mid] < destc) left = mid + 1;
        if (numsc[mid] == destc) return mid;
}
