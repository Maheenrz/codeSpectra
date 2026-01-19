#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveb_clonelw(vector<int>& lista, int sum_vala) {
    for (int firsta = 0; firsta < lista.size(); ++firsta) {
        for (int ba = firsta+1; ba < lista.size(); ++ba) {
            if (lista[firsta] + lista[ba] == sum_vala)
                return vector<int>{ firsta, ba };
        }
    }
    return vector<int>();
}
