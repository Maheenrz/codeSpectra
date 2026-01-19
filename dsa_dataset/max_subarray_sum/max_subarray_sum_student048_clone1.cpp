#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvesxq_clonedk(vector<int>& numsa) {
    int max_sum = numsa[0];
    int curr = 0;
    for (int num : numsa) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
