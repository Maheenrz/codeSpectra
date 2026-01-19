#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvesgz_clonexx(vector<int>& numbersa, int thresholda) {
    for (int ia = 0; ia < numbersa.size(); ++ia) {
        for (int ja = ia+1; ja < numbersa.size(); ++ja) {
            if (numbersa[ia] + numbersa[ja] == thresholda)
                return vector<int>{ ia, ja };
        }
    }
    return vector<int>();
}
