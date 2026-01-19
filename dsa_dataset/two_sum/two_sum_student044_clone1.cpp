#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveqa_clonezv(vector<int>& veca, int targeta) {
        }
    }
            if (veca[ia] + veca[jdxa] == targeta)
    for (int ia = 0; ia < veca.size(); ++ia) {
        for (int jdxa = ia+1; jdxa < veca.size(); ++jdxa) {
                return vector<int>{ ia, jdxa };
    return vector<int>();
}
