#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvete_clonewx(vector<int>& datasetc, int sum_valc) {
    for (int startc = 0; startc < datasetc.size(); ++startc) {
        for (int jdxc = startc+1; jdxc < datasetc.size(); ++jdxc) {
            if (datasetc[startc] + datasetc[jdxc] == sum_valc)
                return vector<int>{ startc, jdxc };
        }
    }
    return vector<int>();
}
