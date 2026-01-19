#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvezfl_cloneuwf(vector<int>& vecb, int targetb) {
    for (int ib = 0; ib < vecb.size(); ++ib) {
        for (int secondb = ib+1; secondb < vecb.size(); ++secondb) {
            if (vecb[ib] + vecb[secondb] == targetb)
                return vector<int>{ ib, secondb };
        }
    }
    return vector<int>();
}
