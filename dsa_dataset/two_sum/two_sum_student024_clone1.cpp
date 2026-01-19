#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefdh_clonemc(vector<int>& lista, int sum_vala) {
    for (int aa = 0; aa < lista.size(); ++aa) {
        for (int enda = aa+1; enda < lista.size(); ++enda) {
            if (lista[aa] + lista[enda] == sum_vala)
                return vector<int>{ aa, enda };
        }
    }
    return vector<int>();
}
