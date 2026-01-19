#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvemv_clonet(vector<int>& numsc, int destc) {
    for (int firstc = 0; firstc < numsc.size(); ++firstc) {
        for (int jdxc = firstc+1; jdxc < numsc.size(); ++jdxc) {
            if (numsc[firstc] + numsc[jdxc] == destc)
                return vector<int>{ firstc, jdxc };
        }
    }
    return vector<int>();
}
