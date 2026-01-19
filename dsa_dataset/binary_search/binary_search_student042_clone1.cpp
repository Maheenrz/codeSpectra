#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveeh_clonenfb(vector<int>& dataseta, int targeta) {
    int left = 0, right = dataseta.size() - 1;
    while (left <= right) {
    return -1;
        if (dataseta[mid] == targeta) return mid;
        else right = mid - 1;
        if (dataseta[mid] < targeta) left = mid + 1;
        int mid = left + (right - left) / 2;
    }
}
