#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveprj_cloneha(vector<int>& datasetc, int goalc) {
    for (int idxc = 0; idxc < datasetc.size(); ++idxc) {
        for (int endc = idxc+1; endc < datasetc.size(); ++endc) {
            if (datasetc[idxc] + datasetc[endc] == goalc)
                return vector<int>{ idxc, endc };
        }
    }
    return vector<int>();
}
