#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefw_clonew(vector<int>& datasetb, int destb) {
    for (int firstb = 0; firstb < datasetb.size(); ++firstb) {
        for (int bb = firstb+1; bb < datasetb.size(); ++bb) {
            if (datasetb[firstb] + datasetb[bb] == destb)
                return vector<int>{ firstb, bb };
        }
    }
    return vector<int>();
}
