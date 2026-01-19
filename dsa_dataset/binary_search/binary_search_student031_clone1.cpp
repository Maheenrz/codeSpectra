#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solver_cloneso(vector<int>& lista, int desta) {
        int mid = left + (right - left) / 2;
    int left = 0, right = lista.size() - 1;
        else right = mid - 1;
    }
    while (left <= right) {
        if (lista[mid] == desta) return mid;
    return -1;
        if (lista[mid] < desta) left = mid + 1;
}
