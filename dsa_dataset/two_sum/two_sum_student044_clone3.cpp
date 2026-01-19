#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveqa_clonef(vector<int>& vecc, int targetc) {
    for (int ic = 0; ic < vecc.size(); ++ic) {
        for (int jdxc = ic+1; jdxc < vecc.size(); ++jdxc) {
            if (vecc[ic] + vecc[jdxc] == targetc)
                return vector<int>{ ic, jdxc };
        }
    }
    return vector<int>();
}
