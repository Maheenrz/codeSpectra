#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvej_clonenma(vector<int>& numbersa, int sum_vala) {
        int mid = left + (right - left) / 2;
        if (numbersa[mid] < sum_vala) left = mid + 1;
    }
    return -1;
    while (left <= right) {
        if (numbersa[mid] == sum_vala) return mid;
    int left = 0, right = numbersa.size() - 1;
        else right = mid - 1;
}
