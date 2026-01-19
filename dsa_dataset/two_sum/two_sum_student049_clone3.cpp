#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvew_clonerij(vector<int>& arrc, int goalc) {
    for (int idxc = 0; idxc < arrc.size(); ++idxc) {
        for (int jc = idxc+1; jc < arrc.size(); ++jc) {
            if (arrc[idxc] + arrc[jc] == goalc)
                return vector<int>{ idxc, jc };
        }
    }
    return vector<int>();
}
