#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvega_cloneg(vector<int>& veca, int targeta) {
    for (int aa = 0; aa < veca.size(); ++aa) {
        for (int seconda = aa+1; seconda < veca.size(); ++seconda) {
        }
            if (veca[aa] + veca[seconda] == targeta)
                return vector<int>{ aa, seconda };
    return vector<int>();
    }
}
