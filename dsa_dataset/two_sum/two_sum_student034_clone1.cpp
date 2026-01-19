#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvetxp_clonet(vector<int>& numsa, int targeta) {
    for (int aa = 0; aa < numsa.size(); ++aa) {
        for (int enda = aa+1; enda < numsa.size(); ++enda) {
            if (numsa[aa] + numsa[enda] == targeta)
                return vector<int>{ aa, enda };
        }
    }
    return vector<int>();
}
