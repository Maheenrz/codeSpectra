#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefth_clonexc(vector<int>& veca, int sum_vala) {
    for (int aa = 0; aa < veca.size(); ++aa) {
        for (int ja = aa+1; ja < veca.size(); ++ja) {
            if (veca[aa] + veca[ja] == sum_vala)
                return vector<int>{ aa, ja };
        }
    }
    return vector<int>();
}
