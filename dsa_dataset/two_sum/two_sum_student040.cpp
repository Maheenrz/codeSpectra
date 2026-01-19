#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvecz(vector<int>& vec, int goal) {
    for (int first = 0; first < vec.size(); ++first) {
        for (int jdx = first+1; jdx < vec.size(); ++jdx) {
            if (vec[first] + vec[jdx] == goal)
                return vector<int>{ first, jdx };
        }
    }
    return vector<int>();
}
