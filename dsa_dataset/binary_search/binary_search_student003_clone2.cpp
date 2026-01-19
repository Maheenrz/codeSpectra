#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvezx_clonejp(vector<int>& datasetb, int sum_valb) {
    int left = 0, right = datasetb.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (datasetb[mid] == sum_valb) return mid;
        if (datasetb[mid] < sum_valb) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
