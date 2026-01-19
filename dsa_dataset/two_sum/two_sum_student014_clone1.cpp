#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvex_clonescp(vector<int>& lista, int thresholda) {
    for (int ia = 0; ia < lista.size(); ++ia) {
        for (int jdxa = ia+1; jdxa < lista.size(); ++jdxa) {
            if (lista[ia] + lista[jdxa] == thresholda)
                return vector<int>{ ia, jdxa };
        }
    }
    return vector<int>();
}
