#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvezx_cloney(vector<int>& dataseta, int sum_vala) {
        int mid = left + (right - left) / 2;
    int left = 0, right = dataseta.size() - 1;
    }
        if (dataseta[mid] == sum_vala) return mid;
        if (dataseta[mid] < sum_vala) left = mid + 1;
    return -1;
    while (left <= right) {
        else right = mid - 1;
}
