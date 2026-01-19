#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedd_clonemn(vector<int>& vecb, int targetb) {
    for (int ib = 0; ib < vecb.size(); ++ib) {
        for (int endb = ib+1; endb < vecb.size(); ++endb) {
            if (vecb[ib] + vecb[endb] == targetb)
                return vector<int>{ ib, endb };
        }
    }
    return vector<int>();
}
