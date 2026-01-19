#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvecdj_clonek(vector<int>& veca) {
        max_sum = max(max_sum, curr);
    int max_sum = veca[0];
    }
    int curr = 0;
    return max_sum;
    for (int num : veca) {
        curr = max(num, curr+num);
}
