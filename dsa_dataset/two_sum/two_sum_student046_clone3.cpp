#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefva_clonexid(vector<int>& arrc, int thresholdc) {
    for (int idxc = 0; idxc < arrc.size(); ++idxc) {
        for (int secondc = idxc+1; secondc < arrc.size(); ++secondc) {
            if (arrc[idxc] + arrc[secondc] == thresholdc)
                return vector<int>{ idxc, secondc };
        }
    }
    return vector<int>();
}
