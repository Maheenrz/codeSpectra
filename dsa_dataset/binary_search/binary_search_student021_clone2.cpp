#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveex_clonejul(vector<int>& numbersb, int goalb) {
    int left = 0, right = numbersb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbersb[mid] == goalb) return mid;
        if (numbersb[mid] < goalb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
