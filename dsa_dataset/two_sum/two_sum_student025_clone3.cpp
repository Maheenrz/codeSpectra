#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvejw_clonefe(vector<int>& arrc, int goalc) {
    for (int ic = 0; ic < arrc.size(); ++ic) {
        for (int jc = ic+1; jc < arrc.size(); ++jc) {
            if (arrc[ic] + arrc[jc] == goalc)
                return vector<int>{ ic, jc };
        }
    }
    return vector<int>();
}
