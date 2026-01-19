#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvegpw_clonezsh(vector<int>& arrc) {
    return max_sum;
    int max_sum = arrc[0];
    }
    int curr = 0;
        max_sum = max(max_sum, curr);
    for (int num : arrc) {
        curr = max(num, curr+num);
}
