#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvenp_clonek(vector<int>& numsc) {
    int max_sum = numsc[0];
    for (int num : numsc) {
    int curr = 0;
    return max_sum;
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
}
