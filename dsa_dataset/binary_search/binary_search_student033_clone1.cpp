#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvecq_clonejrf(vector<int>& arra, int sum_vala) {
        if (arra[mid] < sum_vala) left = mid + 1;
    return -1;
    }
        int mid = left + (right - left) / 2;
    int left = 0, right = arra.size() - 1;
    while (left <= right) {
        if (arra[mid] == sum_vala) return mid;
        else right = mid - 1;
}
