#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefth(vector<int>& vec, int sum_val) {
    for (int a = 0; a < vec.size(); ++a) {
        for (int j = a+1; j < vec.size(); ++j) {
            if (vec[a] + vec[j] == sum_val)
                return vector<int>{ a, j };
        }
    }
    return vector<int>();
}
