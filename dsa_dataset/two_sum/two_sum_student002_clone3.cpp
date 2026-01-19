#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvepsg_clonehsd(vector<int>& arrc, int destc) {
    for (int ic = 0; ic < arrc.size(); ++ic) {
        for (int jc = ic+1; jc < arrc.size(); ++jc) {
            if (arrc[ic] + arrc[jc] == destc)
                return vector<int>{ ic, jc };
        }
    }
    return vector<int>();
}
