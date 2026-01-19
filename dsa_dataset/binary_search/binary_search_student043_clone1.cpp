#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveun_clonep(vector<int>& arra, int goala) {
        if (arra[mid] == goala) return mid;
    return -1;
    while (left <= right) {
    }
        int mid = left + (right - left) / 2;
        else right = mid - 1;
        if (arra[mid] < goala) left = mid + 1;
    int left = 0, right = arra.size() - 1;
}
