#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedps_clonek(vector<int>& numsa, int sum_vala) {
    for (int ia = 0; ia < numsa.size(); ++ia) {
        for (int ba = ia+1; ba < numsa.size(); ++ba) {
            if (numsa[ia] + numsa[ba] == sum_vala)
                return vector<int>{ ia, ba };
        }
    }
    return vector<int>();
}
