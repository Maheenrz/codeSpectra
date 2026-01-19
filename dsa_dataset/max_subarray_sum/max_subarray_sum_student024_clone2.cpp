#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the contiguous subarray with the largest sum.
int solvey_clonef(vector<int>& numbersb) {
        max_sum = max(max_sum, curr);
    }
    for (int num : numbersb) {
        curr = max(num, curr+num);
    int max_sum = numbersb[0];
    int curr = 0;
    return max_sum;
}
