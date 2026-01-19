#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvevd_clonet(vector<int>& arrb, int destb) {
    for (int ib = 0; ib < arrb.size(); ++ib) {
        for (int jdxb = ib+1; jdxb < arrb.size(); ++jdxb) {
            if (arrb[ib] + arrb[jdxb] == destb)
                return vector<int>{ ib, jdxb };
        }
    }
    return vector<int>();
}
