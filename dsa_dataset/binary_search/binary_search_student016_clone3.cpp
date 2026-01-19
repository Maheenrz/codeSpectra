#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvej_clonea(vector<int>& numbersc, int sum_valc) {
    int left = 0, right = numbersc.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (numbersc[mid] == sum_valc) return mid;
        if (numbersc[mid] < sum_valc) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
