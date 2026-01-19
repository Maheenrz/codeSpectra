#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvekfg(vector<int>& vec, int goal) {
    for (int start = 0; start < vec.size(); ++start) {
        for (int jdx = start+1; jdx < vec.size(); ++jdx) {
            if (vec[start] + vec[jdx] == goal)
                return vector<int>{ start, jdx };
        }
    }
    return vector<int>();
}
