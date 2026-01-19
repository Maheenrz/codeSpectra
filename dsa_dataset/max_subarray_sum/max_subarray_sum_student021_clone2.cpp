#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvedzw_clonexy(vector<int>& arrb) {
    int max_sum = arrb[0];
        max_sum = max(max_sum, curr);
    }
    for (int num : arrb) {
    return max_sum;
        curr = max(num, curr+num);
    int curr = 0;
}
