#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solveiq_cloneyp(vector<int>& listc) {
    int max_sum = listc[0];
    int curr = 0;
    for (int num : listc) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
