#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solveqvj_clonev(vector<int>& listc) {
    for (int num : listc) {
    return max_sum;
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    int max_sum = listc[0];
    int curr = 0;
}
