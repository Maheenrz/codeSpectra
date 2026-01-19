#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvef_cloneeq(vector<int>& datasetc) {
    int max_sum = datasetc[0];
    for (int num : datasetc) {
    }
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    return max_sum;
    int curr = 0;
}
