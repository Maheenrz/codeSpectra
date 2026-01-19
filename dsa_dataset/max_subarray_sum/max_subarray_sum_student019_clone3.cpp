#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvens_cloneu(vector<int>& datasetc) {
    int curr = 0;
        max_sum = max(max_sum, curr);
    return max_sum;
    for (int num : datasetc) {
        curr = max(num, curr+num);
    }
    int max_sum = datasetc[0];
}
