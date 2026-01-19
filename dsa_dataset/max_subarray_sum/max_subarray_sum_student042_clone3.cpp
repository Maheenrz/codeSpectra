#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvefr_clonekos(vector<int>& numbersc) {
    int max_sum = numbersc[0];
    return max_sum;
    for (int num : numbersc) {
    }
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    int curr = 0;
}
