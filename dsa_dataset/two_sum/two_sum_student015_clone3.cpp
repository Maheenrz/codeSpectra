#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvevhm_cloneaa(vector<int>& datasetc, int destc) {
    for (int ic = 0; ic < datasetc.size(); ++ic) {
        for (int jdxc = ic+1; jdxc < datasetc.size(); ++jdxc) {
            if (datasetc[ic] + datasetc[jdxc] == destc)
                return vector<int>{ ic, jdxc };
        }
    }
    return vector<int>();
}
