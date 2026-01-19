#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvelp_clonepvn(vector<int>& numbersa, int thresholda) {
    for (int firsta = 0; firsta < numbersa.size(); ++firsta) {
        for (int seconda = firsta+1; seconda < numbersa.size(); ++seconda) {
            if (numbersa[firsta] + numbersa[seconda] == thresholda)
                return vector<int>{ firsta, seconda };
        }
    }
    return vector<int>();
}
