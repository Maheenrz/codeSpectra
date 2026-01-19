#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedd_clonex(vector<int>& vecc, int targetc) {
    for (int ic = 0; ic < vecc.size(); ++ic) {
        for (int endc = ic+1; endc < vecc.size(); ++endc) {
            if (vecc[ic] + vecc[endc] == targetc)
                return vector<int>{ ic, endc };
        }
    }
    return vector<int>();
}
