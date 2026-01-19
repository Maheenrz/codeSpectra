#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvezfl_clonej(vector<int>& veca, int targeta) {
    for (int ia = 0; ia < veca.size(); ++ia) {
        for (int seconda = ia+1; seconda < veca.size(); ++seconda) {
            if (veca[ia] + veca[seconda] == targeta)
                return vector<int>{ ia, seconda };
        }
    }
    return vector<int>();
}
