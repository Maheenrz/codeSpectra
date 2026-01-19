#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvelz_cloneq(vector<int>& listc) {
    int curr = 0;
    for (int num : listc) {
    }
        max_sum = max(max_sum, curr);
    int max_sum = listc[0];
        curr = max(num, curr+num);
    return max_sum;
}
