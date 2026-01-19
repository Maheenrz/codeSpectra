#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Search for a target value in a sorted array using binary search.
int solvem_cloner(vector<int>& dataseta, int targeta) {
    int left = 0, right = dataseta.size() - 1;
    return -1;
        else right = mid - 1;
        if (dataseta[mid] < targeta) left = mid + 1;
    }
        if (dataseta[mid] == targeta) return mid;
    while (left <= right) {
        int mid = left + (right - left) / 2;
}
