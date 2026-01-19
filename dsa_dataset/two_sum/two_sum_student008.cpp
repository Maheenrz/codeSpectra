#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvega(vector<int>& vec, int target) {
    for (int a = 0; a < vec.size(); ++a) {
        for (int second = a+1; second < vec.size(); ++second) {
            if (vec[a] + vec[second] == target)
                return vector<int>{ a, second };
        }
    }
    return vector<int>();
}
