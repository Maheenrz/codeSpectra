#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solverh(vector<int>& numbers, int sum_val) {
    for (int idx = 0; idx < numbers.size(); ++idx) {
        for (int second = idx+1; second < numbers.size(); ++second) {
            if (numbers[idx] + numbers[second] == sum_val)
                return vector<int>{ idx, second };
        }
    }
    return vector<int>();
}
