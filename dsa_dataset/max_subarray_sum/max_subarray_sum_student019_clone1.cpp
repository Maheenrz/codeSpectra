#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvens_cloneu(vector<int>& dataseta) {
    int curr = 0;
        max_sum = max(max_sum, curr);
    return max_sum;
    int max_sum = dataseta[0];
    }
    for (int num : dataseta) {
        curr = max(num, curr+num);
}
