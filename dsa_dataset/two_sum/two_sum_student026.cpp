#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvenx(vector<int>& numbers, int target) {
    for (int a = 0; a < numbers.size(); ++a) {
        for (int jdx = a+1; jdx < numbers.size(); ++jdx) {
            if (numbers[a] + numbers[jdx] == target)
                return vector<int>{ a, jdx };
        }
    }
    return vector<int>();
}
