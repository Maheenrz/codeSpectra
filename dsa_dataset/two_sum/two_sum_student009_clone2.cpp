#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvesgz_clonee(vector<int>& numbersb, int thresholdb) {
    for (int ib = 0; ib < numbersb.size(); ++ib) {
        for (int jb = ib+1; jb < numbersb.size(); ++jb) {
            if (numbersb[ib] + numbersb[jb] == thresholdb)
                return vector<int>{ ib, jb };
        }
    }
    return vector<int>();
}
