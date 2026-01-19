#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvel_clonein(vector<int>& numsa, int sum_vala) {
    int left = 0, right = numsa.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numsa[mid] == sum_vala) return mid;
        if (numsa[mid] < sum_vala) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
