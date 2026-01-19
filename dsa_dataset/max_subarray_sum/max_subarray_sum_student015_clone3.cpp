#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solveiqo_cloner(vector<int>& datasetc) {
    for (int num : datasetc) {
        curr = max(num, curr+num);
    return max_sum;
    }
        max_sum = max(max_sum, curr);
    int max_sum = datasetc[0];
    int curr = 0;
}
