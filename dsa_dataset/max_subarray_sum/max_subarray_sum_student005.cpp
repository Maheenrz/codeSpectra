#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the contiguous subarray with the largest sum.
int solvegpw(vector<int>& arr) {
    int max_sum = arr[0];
    int curr = 0;
    for (int num : arr) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
