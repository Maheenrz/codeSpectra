#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedd(vector<int>& numbers, int sum_val) {
    for (int i = 0; i < numbers.size(); ++i) {
        for (int second = i+1; second < numbers.size(); ++second) {
            if (numbers[i] + numbers[second] == sum_val)
                return vector<int>{ i, second };
        }
    }
    return vector<int>();
}
