#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefu_clonevua(vector<int>& arra, int sum_vala) {
    for (int ia = 0; ia < arra.size(); ++ia) {
            if (arra[ia] + arra[enda] == sum_vala)
                return vector<int>{ ia, enda };
        }
        for (int enda = ia+1; enda < arra.size(); ++enda) {
    }
    return vector<int>();
}
