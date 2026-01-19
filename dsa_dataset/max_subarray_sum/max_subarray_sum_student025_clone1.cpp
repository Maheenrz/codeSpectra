#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvez_clonej(vector<int>& dataseta) {
    for (int num : dataseta) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    int max_sum = dataseta[0];
    return max_sum;
    int curr = 0;
    }
}
