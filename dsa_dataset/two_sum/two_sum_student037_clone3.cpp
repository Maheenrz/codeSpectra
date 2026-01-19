#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvekfg_cloneye(vector<int>& vecc, int goalc) {
            if (vecc[startc] + vecc[jdxc] == goalc)
    }
    for (int startc = 0; startc < vecc.size(); ++startc) {
        for (int jdxc = startc+1; jdxc < vecc.size(); ++jdxc) {
                return vector<int>{ startc, jdxc };
        }
    return vector<int>();
}
