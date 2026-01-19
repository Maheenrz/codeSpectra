#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvec_cloneg(vector<int>& vecc, int sum_valc) {
    return -1;
        if (vecc[mid] < sum_valc) left = mid + 1;
    while (left <= right) {
        if (vecc[mid] == sum_valc) return mid;
    }
        else right = mid - 1;
        int mid = left + (right - left) / 2;
    int left = 0, right = vecc.size() - 1;
}
