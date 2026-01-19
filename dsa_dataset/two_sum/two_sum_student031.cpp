#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvexj(vector<int>& vec, int dest) {
    for (int a = 0; a < vec.size(); ++a) {
        for (int b = a+1; b < vec.size(); ++b) {
            if (vec[a] + vec[b] == dest)
                return vector<int>{ a, b };
        }
    }
    return vector<int>();
}
