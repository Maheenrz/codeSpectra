#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvetxp_clonej(vector<int>& numsa) {
        max_sum = max(max_sum, curr);
    int curr = 0;
    for (int num : numsa) {
        curr = max(num, curr+num);
    int max_sum = numsa[0];
    return max_sum;
    }
}
