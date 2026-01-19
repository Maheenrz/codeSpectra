#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solveiq_clonenv(vector<int>& listb) {
    int max_sum = listb[0];
    int curr = 0;
    for (int num : listb) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
