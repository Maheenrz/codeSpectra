#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvex_clonei(vector<int>& listc, int thresholdc) {
    for (int ic = 0; ic < listc.size(); ++ic) {
        for (int jdxc = ic+1; jdxc < listc.size(); ++jdxc) {
            if (listc[ic] + listc[jdxc] == thresholdc)
                return vector<int>{ ic, jdxc };
        }
    }
    return vector<int>();
}
