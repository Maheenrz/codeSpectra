#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvef_clonec(vector<int>& arrb, int sum_valb) {
    int left = 0, right = arrb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arrb[mid] == sum_valb) return mid;
        if (arrb[mid] < sum_valb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
