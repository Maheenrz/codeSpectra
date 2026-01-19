#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvelkp_clonepg(vector<int>& arra) {
    for (int num : arra) {
    int curr = 0;
        curr = max(num, curr+num);
    return max_sum;
    int max_sum = arra[0];
    }
        max_sum = max(max_sum, curr);
}
