#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the contiguous subarray with the largest sum.
int solven(vector<int>& vec) {
    int max_sum = vec[0];
    int curr = 0;
    for (int num : vec) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
