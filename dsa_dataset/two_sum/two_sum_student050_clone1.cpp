#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvebl_clonejsm(vector<int>& veca, int sum_vala) {
    for (int firsta = 0; firsta < veca.size(); ++firsta) {
        for (int jdxa = firsta+1; jdxa < veca.size(); ++jdxa) {
            if (veca[firsta] + veca[jdxa] == sum_vala)
                return vector<int>{ firsta, jdxa };
        }
    }
    return vector<int>();
}
