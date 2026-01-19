#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvevhm_cloneyto(vector<int>& datasetb, int destb) {
    for (int ib = 0; ib < datasetb.size(); ++ib) {
        for (int jdxb = ib+1; jdxb < datasetb.size(); ++jdxb) {
            if (datasetb[ib] + datasetb[jdxb] == destb)
                return vector<int>{ ib, jdxb };
        }
    }
    return vector<int>();
}
