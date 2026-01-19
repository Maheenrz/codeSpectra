#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvebzg_cloneys(vector<int>& numbersb, int targetb) {
    int left = 0, right = numbersb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbersb[mid] == targetb) return mid;
        if (numbersb[mid] < targetb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
