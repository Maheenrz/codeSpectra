#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvezfl_clonecd(vector<int>& vecc, int targetc) {
    for (int ic = 0; ic < vecc.size(); ++ic) {
        for (int secondc = ic+1; secondc < vecc.size(); ++secondc) {
            if (vecc[ic] + vecc[secondc] == targetc)
                return vector<int>{ ic, secondc };
        }
    }
    return vector<int>();
}
