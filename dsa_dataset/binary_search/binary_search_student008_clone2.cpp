#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvec_clonen(vector<int>& vecb, int sum_valb) {
    int left = 0, right = vecb.size() - 1;
    return -1;
    }
        if (vecb[mid] == sum_valb) return mid;
        else right = mid - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (vecb[mid] < sum_valb) left = mid + 1;
}
