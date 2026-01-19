#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvenx_clonevw(vector<int>& numbersa, int targeta) {
    for (int aa = 0; aa < numbersa.size(); ++aa) {
        for (int jdxa = aa+1; jdxa < numbersa.size(); ++jdxa) {
            if (numbersa[aa] + numbersa[jdxa] == targeta)
                return vector<int>{ aa, jdxa };
        }
    }
    return vector<int>();
}
