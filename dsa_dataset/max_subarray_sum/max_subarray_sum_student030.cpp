#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the contiguous subarray with the largest sum.
int solvekek(vector<int>& numbers) {
    int max_sum = numbers[0];
    int curr = 0;
    for (int num : numbers) {
        curr = max(num, curr+num);
        max_sum = max(max_sum, curr);
    }
    return max_sum;
}
