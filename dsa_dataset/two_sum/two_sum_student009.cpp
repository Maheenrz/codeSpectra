#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvesgz(vector<int>& numbers, int threshold) {
    for (int i = 0; i < numbers.size(); ++i) {
        for (int j = i+1; j < numbers.size(); ++j) {
            if (numbers[i] + numbers[j] == threshold)
                return vector<int>{ i, j };
        }
    }
    return vector<int>();
}
