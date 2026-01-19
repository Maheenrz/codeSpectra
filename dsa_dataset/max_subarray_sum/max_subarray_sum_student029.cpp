#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the contiguous subarray with the largest sum.
int solveah(vector<int>& dataset) {
    int max_sum = dataset[0];
    int curr = 0;
    for (int num : dataset) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
