#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefth_clonepdj(vector<int>& vecb, int sum_valb) {
    for (int ab = 0; ab < vecb.size(); ++ab) {
        for (int jb = ab+1; jb < vecb.size(); ++jb) {
            if (vecb[ab] + vecb[jb] == sum_valb)
                return vector<int>{ ab, jb };
        }
    }
    return vector<int>();
}
