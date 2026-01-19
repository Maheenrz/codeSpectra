#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveikr_clonekpu(vector<int>& numsb, int targetb) {
    for (int ib = 0; ib < numsb.size(); ++ib) {
        for (int jb = ib+1; jb < numsb.size(); ++jb) {
            if (numsb[ib] + numsb[jb] == targetb)
                return vector<int>{ ib, jb };
        }
    }
    return vector<int>();
}
