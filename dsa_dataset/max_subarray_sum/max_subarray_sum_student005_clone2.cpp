#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvegpw_clonerj(vector<int>& arrb) {
    int max_sum = arrb[0];
    int curr = 0;
    for (int num : arrb) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
