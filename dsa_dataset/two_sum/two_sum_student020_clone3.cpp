#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedhc_clonein(vector<int>& arrc, int destc) {
    for (int idxc = 0; idxc < arrc.size(); ++idxc) {
        for (int secondc = idxc+1; secondc < arrc.size(); ++secondc) {
            if (arrc[idxc] + arrc[secondc] == destc)
                return vector<int>{ idxc, secondc };
        }
    }
    return vector<int>();
}
