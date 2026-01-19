#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvex_cloneulu(vector<int>& listb, int thresholdb) {
    for (int ib = 0; ib < listb.size(); ++ib) {
        for (int jdxb = ib+1; jdxb < listb.size(); ++jdxb) {
            if (listb[ib] + listb[jdxb] == thresholdb)
                return vector<int>{ ib, jdxb };
        }
    }
    return vector<int>();
}
