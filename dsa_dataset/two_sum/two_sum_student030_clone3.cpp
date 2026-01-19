#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedmg_clonep(vector<int>& arrc, int sum_valc) {
    for (int idxc = 0; idxc < arrc.size(); ++idxc) {
        for (int bc = idxc+1; bc < arrc.size(); ++bc) {
            if (arrc[idxc] + arrc[bc] == sum_valc)
                return vector<int>{ idxc, bc };
        }
    }
    return vector<int>();
}
