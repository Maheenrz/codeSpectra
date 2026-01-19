#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvepsg_clonec(vector<int>& arrb, int destb) {
    for (int ib = 0; ib < arrb.size(); ++ib) {
        for (int jb = ib+1; jb < arrb.size(); ++jb) {
            if (arrb[ib] + arrb[jb] == destb)
                return vector<int>{ ib, jb };
        }
    }
    return vector<int>();
}
