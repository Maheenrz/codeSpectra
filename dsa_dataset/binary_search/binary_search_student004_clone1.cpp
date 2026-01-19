#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvefh_clonec(vector<int>& lista, int goala) {
    return -1;
        int mid = left + (right - left) / 2;
        else right = mid - 1;
        if (lista[mid] < goala) left = mid + 1;
    int left = 0, right = lista.size() - 1;
        if (lista[mid] == goala) return mid;
    while (left <= right) {
    }
}
