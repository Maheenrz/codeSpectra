#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvehcd_cloneat(vector<int>& arrc, int sum_valc) {
    for (int idxc = 0; idxc < arrc.size(); ++idxc) {
        for (int jdxc = idxc+1; jdxc < arrc.size(); ++jdxc) {
            if (arrc[idxc] + arrc[jdxc] == sum_valc)
                return vector<int>{ idxc, jdxc };
        }
    }
    return vector<int>();
}
