#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvenp_clonehk(vector<int>& numsa) {
    for (int num : numsa) {
    return max_sum;
        max_sum = max(max_sum, curr);
    int curr = 0;
    int max_sum = numsa[0];
        curr = max(num, curr+num);
    }
}
