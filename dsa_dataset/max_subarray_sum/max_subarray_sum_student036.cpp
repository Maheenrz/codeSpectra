#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the contiguous subarray with the largest sum.
int solvead(vector<int>& list) {
    int max_sum = list[0];
    int curr = 0;
    for (int num : list) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
