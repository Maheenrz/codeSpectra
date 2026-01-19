#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solveqt_clonee(vector<int>& lista, int targeta) {
    int left = 0, right = lista.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (lista[mid] == targeta) return mid;
        if (lista[mid] < targeta) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
