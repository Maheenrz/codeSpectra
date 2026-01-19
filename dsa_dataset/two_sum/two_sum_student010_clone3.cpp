#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveycb_clonehft(vector<int>& numsc, int sum_valc) {
    for (int ac = 0; ac < numsc.size(); ++ac) {
        for (int jdxc = ac+1; jdxc < numsc.size(); ++jdxc) {
            if (numsc[ac] + numsc[jdxc] == sum_valc)
                return vector<int>{ ac, jdxc };
        }
    }
    return vector<int>();
}
