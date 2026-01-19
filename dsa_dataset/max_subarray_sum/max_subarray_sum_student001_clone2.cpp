#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solveow_clonexh(vector<int>& listb) {
    int curr = 0;
        curr = max(num, curr+num);
    }
    int max_sum = listb[0];
        max_sum = max(max_sum, curr);
    for (int num : listb) {
    return max_sum;
}
