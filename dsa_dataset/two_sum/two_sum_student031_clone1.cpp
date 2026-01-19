#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvexj_cloneynm(vector<int>& veca, int desta) {
    for (int aa = 0; aa < veca.size(); ++aa) {
        for (int ba = aa+1; ba < veca.size(); ++ba) {
            if (veca[aa] + veca[ba] == desta)
                return vector<int>{ aa, ba };
        }
    }
    return vector<int>();
}
