#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvexj_clonelyu(vector<int>& vecc, int destc) {
    for (int ac = 0; ac < vecc.size(); ++ac) {
        for (int bc = ac+1; bc < vecc.size(); ++bc) {
            if (vecc[ac] + vecc[bc] == destc)
                return vector<int>{ ac, bc };
        }
    }
    return vector<int>();
}
