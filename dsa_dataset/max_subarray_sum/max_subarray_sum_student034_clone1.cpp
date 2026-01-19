#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solven_clonebe(vector<int>& veca) {
    int max_sum = veca[0];
    int curr = 0;
    for (int num : veca) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
