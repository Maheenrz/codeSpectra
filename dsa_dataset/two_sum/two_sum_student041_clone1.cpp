#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvexg_clonehj(vector<int>& lista, int sum_vala) {
    for (int starta = 0; starta < lista.size(); ++starta) {
        for (int enda = starta+1; enda < lista.size(); ++enda) {
            if (lista[starta] + lista[enda] == sum_vala)
                return vector<int>{ starta, enda };
        }
    }
    return vector<int>();
}
