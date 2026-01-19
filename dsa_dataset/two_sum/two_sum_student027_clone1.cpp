#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveikr_cloneuvk(vector<int>& numsa, int targeta) {
    for (int ia = 0; ia < numsa.size(); ++ia) {
        for (int ja = ia+1; ja < numsa.size(); ++ja) {
            if (numsa[ia] + numsa[ja] == targeta)
                return vector<int>{ ia, ja };
        }
    }
    return vector<int>();
}
