#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvenx_clonez(vector<int>& numbersc, int targetc) {
    for (int ac = 0; ac < numbersc.size(); ++ac) {
        for (int jdxc = ac+1; jdxc < numbersc.size(); ++jdxc) {
            if (numbersc[ac] + numbersc[jdxc] == targetc)
                return vector<int>{ ac, jdxc };
        }
    }
    return vector<int>();
}
