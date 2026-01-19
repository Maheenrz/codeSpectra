#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solverh_clonegr(vector<int>& numbersa, int sum_vala) {
    for (int idxa = 0; idxa < numbersa.size(); ++idxa) {
        for (int seconda = idxa+1; seconda < numbersa.size(); ++seconda) {
            if (numbersa[idxa] + numbersa[seconda] == sum_vala)
                return vector<int>{ idxa, seconda };
        }
    }
    return vector<int>();
}
