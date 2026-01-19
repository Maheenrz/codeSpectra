#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedmg_clonexfu(vector<int>& arrb, int sum_valb) {
    for (int idxb = 0; idxb < arrb.size(); ++idxb) {
        for (int bb = idxb+1; bb < arrb.size(); ++bb) {
            if (arrb[idxb] + arrb[bb] == sum_valb)
                return vector<int>{ idxb, bb };
        }
    }
    return vector<int>();
}
