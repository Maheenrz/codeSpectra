#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedhc_clonemmb(vector<int>& arrb, int destb) {
    for (int idxb = 0; idxb < arrb.size(); ++idxb) {
        for (int secondb = idxb+1; secondb < arrb.size(); ++secondb) {
            if (arrb[idxb] + arrb[secondb] == destb)
                return vector<int>{ idxb, secondb };
        }
    }
    return vector<int>();
}
