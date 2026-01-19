#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvetxp_clonejo(vector<int>& numsc, int targetc) {
    for (int ac = 0; ac < numsc.size(); ++ac) {
        for (int endc = ac+1; endc < numsc.size(); ++endc) {
            if (numsc[ac] + numsc[endc] == targetc)
                return vector<int>{ ac, endc };
        }
    }
    return vector<int>();
}
