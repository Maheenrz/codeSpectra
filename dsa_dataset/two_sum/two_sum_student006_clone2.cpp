#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedd_cloneil(vector<int>& numbersb, int sum_valb) {
    for (int ib = 0; ib < numbersb.size(); ++ib) {
        for (int secondb = ib+1; secondb < numbersb.size(); ++secondb) {
            if (numbersb[ib] + numbersb[secondb] == sum_valb)
                return vector<int>{ ib, secondb };
        }
    }
    return vector<int>();
}
