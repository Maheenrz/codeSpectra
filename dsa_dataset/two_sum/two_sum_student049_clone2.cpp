#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvew_clonexvo(vector<int>& arrb, int goalb) {
    for (int idxb = 0; idxb < arrb.size(); ++idxb) {
            if (arrb[idxb] + arrb[jb] == goalb)
    }
        for (int jb = idxb+1; jb < arrb.size(); ++jb) {
                return vector<int>{ idxb, jb };
        }
    return vector<int>();
}
