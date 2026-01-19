#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvefth_clonefe(vector<int>& lista, int sum_vala) {
        int mid = left + (right - left) / 2;
        if (lista[mid] == sum_vala) return mid;
    int left = 0, right = lista.size() - 1;
    while (left <= right) {
        if (lista[mid] < sum_vala) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
