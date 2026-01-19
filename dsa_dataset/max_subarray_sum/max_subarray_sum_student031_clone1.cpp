#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solveqvj_cloneox(vector<int>& lista) {
    int max_sum = lista[0];
    int curr = 0;
    for (int num : lista) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
