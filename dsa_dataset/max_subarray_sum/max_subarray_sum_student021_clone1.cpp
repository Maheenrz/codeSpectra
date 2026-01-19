#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvedzw_clonegya(vector<int>& arra) {
    return max_sum;
    int curr = 0;
    int max_sum = arra[0];
        max_sum = max(max_sum, curr);
    for (int num : arra) {
    }
        curr = max(num, curr+num);
}
