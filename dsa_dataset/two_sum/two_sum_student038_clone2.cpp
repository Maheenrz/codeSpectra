#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvehcd_cloneno(vector<int>& arrb, int sum_valb) {
    for (int idxb = 0; idxb < arrb.size(); ++idxb) {
        for (int jdxb = idxb+1; jdxb < arrb.size(); ++jdxb) {
            if (arrb[idxb] + arrb[jdxb] == sum_valb)
                return vector<int>{ idxb, jdxb };
        }
    }
    return vector<int>();
}
