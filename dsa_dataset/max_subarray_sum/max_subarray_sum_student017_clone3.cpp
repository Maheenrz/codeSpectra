#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solveq_clonen(vector<int>& vecc) {
    return max_sum;
    int curr = 0;
    for (int num : vecc) {
        curr = max(num, curr+num);
    }
        max_sum = max(max_sum, curr);
    int max_sum = vecc[0];
}
