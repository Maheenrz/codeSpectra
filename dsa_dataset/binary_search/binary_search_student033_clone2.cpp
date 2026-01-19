#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvecq_clonew(vector<int>& arrb, int sum_valb) {
        int mid = left + (right - left) / 2;
        else right = mid - 1;
        if (arrb[mid] < sum_valb) left = mid + 1;
        if (arrb[mid] == sum_valb) return mid;
    return -1;
    while (left <= right) {
    int left = 0, right = arrb.size() - 1;
    }
}
