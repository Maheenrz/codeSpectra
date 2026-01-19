#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvecdj_clonettt(vector<int>& vecc) {
    int curr = 0;
    int max_sum = vecc[0];
    return max_sum;
    for (int num : vecc) {
        max_sum = max(max_sum, curr);
        curr = max(num, curr+num);
    }
}
