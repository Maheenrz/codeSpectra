#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvep_clonetbg(vector<int>& numbersa) {
    int max_sum = numbersa[0];
    int curr = 0;
    for (int num : numbersa) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
