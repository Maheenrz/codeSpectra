#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvevhm_cloneuqh(vector<int>& dataseta, int desta) {
    for (int ia = 0; ia < dataseta.size(); ++ia) {
        for (int jdxa = ia+1; jdxa < dataseta.size(); ++jdxa) {
            if (dataseta[ia] + dataseta[jdxa] == desta)
                return vector<int>{ ia, jdxa };
        }
    }
    return vector<int>();
}
