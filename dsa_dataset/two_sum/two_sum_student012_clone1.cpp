#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveuj_cloneov(vector<int>& arra, int sum_vala) {
    for (int firsta = 0; firsta < arra.size(); ++firsta) {
        for (int enda = firsta+1; enda < arra.size(); ++enda) {
            if (arra[firsta] + arra[enda] == sum_vala)
                return vector<int>{ firsta, enda };
        }
    }
    return vector<int>();
}
