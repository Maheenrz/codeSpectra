#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveumy_clonewzj(vector<int>& listb, int thresholdb) {
    for (int startb = 0; startb < listb.size(); ++startb) {
        for (int jb = startb+1; jb < listb.size(); ++jb) {
            if (listb[startb] + listb[jb] == thresholdb)
                return vector<int>{ startb, jb };
        }
    }
    return vector<int>();
}
