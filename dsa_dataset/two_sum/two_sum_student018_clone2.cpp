#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvehnj_clonehe(vector<int>& datasetb, int goalb) {
    for (int startb = 0; startb < datasetb.size(); ++startb) {
        for (int bb = startb+1; bb < datasetb.size(); ++bb) {
            if (datasetb[startb] + datasetb[bb] == goalb)
                return vector<int>{ startb, bb };
        }
    }
    return vector<int>();
}
