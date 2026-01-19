#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvesyb_clonel(vector<int>& numbersa, int goala) {
    int left = 0, right = numbersa.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbersa[mid] == goala) return mid;
        if (numbersa[mid] < goala) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
