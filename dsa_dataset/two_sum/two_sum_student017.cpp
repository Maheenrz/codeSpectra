#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvetga(vector<int>& numbers, int goal) {
    for (int idx = 0; idx < numbers.size(); ++idx) {
        for (int end = idx+1; end < numbers.size(); ++end) {
            if (numbers[idx] + numbers[end] == goal)
                return vector<int>{ idx, end };
        }
    }
    return vector<int>();
}
