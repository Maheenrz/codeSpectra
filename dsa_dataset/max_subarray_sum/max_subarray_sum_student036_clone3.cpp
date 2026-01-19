#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvead_clonevq(vector<int>& listc) {
    for (int num : listc) {
    return max_sum;
    }
        curr = max(num, curr+num);
    int curr = 0;
    int max_sum = listc[0];
        max_sum = max(max_sum, curr);
}
