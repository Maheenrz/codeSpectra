#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solverh_cloneuj(vector<int>& numbersb, int sum_valb) {
    for (int idxb = 0; idxb < numbersb.size(); ++idxb) {
        for (int secondb = idxb+1; secondb < numbersb.size(); ++secondb) {
            if (numbersb[idxb] + numbersb[secondb] == sum_valb)
                return vector<int>{ idxb, secondb };
        }
    }
    return vector<int>();
}
