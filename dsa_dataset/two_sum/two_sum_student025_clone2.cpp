#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvejw_clonenq(vector<int>& arrb, int goalb) {
    for (int ib = 0; ib < arrb.size(); ++ib) {
        for (int jb = ib+1; jb < arrb.size(); ++jb) {
            if (arrb[ib] + arrb[jb] == goalb)
                return vector<int>{ ib, jb };
        }
    }
    return vector<int>();
}
