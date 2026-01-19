#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvet_clonenu(vector<int>& dataseta, int goala) {
    int left = 0, right = dataseta.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (dataseta[mid] == goala) return mid;
        if (dataseta[mid] < goala) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
