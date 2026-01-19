#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedd_clonegij(vector<int>& numbersa, int sum_vala) {
    for (int ia = 0; ia < numbersa.size(); ++ia) {
        for (int seconda = ia+1; seconda < numbersa.size(); ++seconda) {
            if (numbersa[ia] + numbersa[seconda] == sum_vala)
                return vector<int>{ ia, seconda };
        }
    }
    return vector<int>();
}
