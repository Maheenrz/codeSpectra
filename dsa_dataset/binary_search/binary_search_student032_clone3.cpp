#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvefth_clonedtv(vector<int>& listc, int sum_valc) {
    int left = 0, right = listc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (listc[mid] == sum_valc) return mid;
        if (listc[mid] < sum_valc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
