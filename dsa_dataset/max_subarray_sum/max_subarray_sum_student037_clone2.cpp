#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvelz_clonew(vector<int>& listb) {
    return max_sum;
    int max_sum = listb[0];
    int curr = 0;
    for (int num : listb) {
        max_sum = max(max_sum, curr);
    }
        curr = max(num, curr+num);
}
