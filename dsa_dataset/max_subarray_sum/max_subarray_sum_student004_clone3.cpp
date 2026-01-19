#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvebzx_clonep(vector<int>& vecc) {
    int max_sum = vecc[0];
    int curr = 0;
    for (int num : vecc) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
