#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveprj_clonefrz(vector<int>& datasetb, int goalb) {
    for (int idxb = 0; idxb < datasetb.size(); ++idxb) {
        for (int endb = idxb+1; endb < datasetb.size(); ++endb) {
            if (datasetb[idxb] + datasetb[endb] == goalb)
                return vector<int>{ idxb, endb };
        }
    }
    return vector<int>();
}
